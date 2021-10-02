import functools
import flask
import string, random
from . import osf

import os,sys

#
# Our webserver-unaware packages for processing things
import ure

uploaddir = 'tmpfiles'

bp = flask.Blueprint('import', __name__, url_prefix='/import')


@bp.route('/googledoc', methods=('GET', 'POST'))
def googledoc():
    return(flask.render_template('import/googledoc.html'))


@bp.route('/docx', methods=('GET', 'POST'))
def docx():
    if flask.request.method == 'POST':
        return(docx_import())
    else:
        return(flask.render_template('import/docx.html'))


@bp.route('/process_docx_upload', methods=['POST'])
def process_docx_upload():
    docx = flask.request.files['upload-docx']
    # -- generate a filename
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + '.docx'
    
    docx.save(uploaddir + '/' + filename)
    return({
        'filename': docx.filename, 
        'id': filename, 
    })
    return(f"<html><body><h1>SOMETHING HAPPENED</h1><h2>{docx}</h2></body></html>")
    #return(flask.render_template('import/docx.html'))


@bp.route('/import_docx', methods=['POST'])
def docx_import():

    # 
    # Parameter Validation
    #
    parameters = {k:None if v == '' else v for k,v in flask.request.form.items()}
    #
    # jQuery.serialize is dumb. Checked checkboxes are encoded as empty hash values, and unchecked checkboxes are not present in the paraemeter list.
    # So we fix that here
    for checkboxparam in ['overwrite', 'deleteold']:
        parameters[checkboxparam] = checkboxparam in parameters

    for reqparam in ['osf-project-id', 'fileid']:
        if not parameters[reqparam]:
            raise Exception(f"Required parameter {reqparam} not defined in form submission. Please report this to tech support.")

    exporter = ure.exporter.from_file(
        uploaddir + '/' + parameters['fileid'], 
        section_break=parameters['section-break-policy'],
        page_break=parameters['page-break-policy'],
        h1_break=parameters['h1-policy'],
        h2_break=parameters['h2-policy'],        
    )
    projectid = parameters['osf-project-id']
    projectname = parameters['osf-project-name']

    overwrite = parameters['overwrite']
    deleteold = parameters['deleteold']

    # Nodelookup is a mapping of node id -> name for all nodes
    nodelookup = {projectid: projectname}

    # Verify that we are logged in
    ping = osf.getme(refresh=True)
    if 'errors' in ping:
        return(ping)

    # Get the existing subcomponents
    childjs = osf.osfgetdata(f"/nodes/{projectid}/children/", fetch_all=True)
    existingnodes = {}
    for jswiki in childjs:
        existingnodes[jswiki['attributes']['title']] = jswiki['id']
        nodelookup[jswiki['id']] = jswiki['attributes']['title']

    allcomponents = exporter.markdown    
    root_project = allcomponents.pop(0)    
    root_wikis = root_project[1]
    
    # Now render all the wikis for the main project
    wikiactions = render_wikis(projectid, root_wikis, overwrite=overwrite, deleteold=deleteold)
    componentactions = {
        'created': [],
        'updated': [],
        'deleted': [],
        'ignored': [],
    }

    # Now handle all the components
    for component_name, compwikis in allcomponents:
        
        if component_name in existingnodes:
            newactions = render_wikis(existingnodes[component_name], compwikis, overwrite=overwrite, deleteold=deleteold)
            for k,v in newactions.items():
                wikiactions[k].extend(v)
            componentactions['updated'].append([ existingnodes[component_name], component_name])
            del existingnodes[component_name]
        else:
            new_component = osf.osfpost(
                f'/nodes/{projectid}/children/', 
                {
                    'type': 'nodes',
                    'title': component_name,
                    'category': 'software'
                }
            )
            # at the new component to the name lookup hash
            nodelookup[new_component['data']['id']] = component_name
            # add it to the action log
            componentactions['created'].append([ new_component['data']['id'], component_name])
            # render the new wikis
            newactions = render_wikis(new_component['data']['id'], compwikis, overwrite=overwrite, deleteold=deleteold)
            for k,v in newactions.items():
                wikiactions[k].extend(v)
            
    # now handle untouched components, which may be deleted or ignored
    if existingnodes:
        if deleteold :
            for nodename, nodeid in existingnodes.items():
                osf.osfdelete(f'/nodes/{nodeid}/')
                componentactions['deleted'].append([nodeid, nodename])
        else:
            for nodename, nodeid in existingnodes.items():
                componentactions['ignored'].append([nodeid, nodename])

    return({
        'rootnodeid': projectid,
        'rootnodename': projectname,
        'nodemap': nodelookup,
        'wikiactions': wikiactions,
        'componentactions': componentactions,
    })
    
def render_wikis(nodeid, wikis, overwrite=True, deleteold=False):
    """ Uses the osf module interface to create/update/delete the wiki pages
    
    Args:
        nodeid (str): The node whose wikis we are rendering
        wikis (list(tuple)): A list of 2-element tuples (wiki_name, wiki_content) that represents all the wikis to be set for this node.
        overwrite (bool): If True, whether to overwrite existing wikis. Default is True.
        deleteold (bool): If True, delete any existing wikis that are not updated. Default is False. 
    Returns: dict of actions performed with keys ('created', 'updated', 'deleted')
    """
    actions = {'created': [], 'updated': [], 'deleted': [], 'ignored': [] }

    wikijs = osf.osfgetdata(f"/nodes/{nodeid}/wikis/", fetch_all=True)
    existingwikis = {}
    for jswiki in wikijs:
        existingwikis[jswiki['attributes']['name']] = jswiki['id']

    # Handle the Home wiki
    home_wiki = wikis.pop(0)
    if existingwikis:
        hometag = 'home' if 'home' in existingwikis else 'Home'
        if hometag not in existingwikis:
            raise Exception(f"Cannot identify the home wiki. Wiki names are: '" + "','".join(existingwikis) + "'")
        if not overwrite:
            actions['ignored'].append([nodeid, 'home', existingwikis[hometag]])
        else:                
            # post updated content to the wiki
            resp = osf.osfpost(f'/wikis/{existingwikis[hometag]}/versions/', {
                'type': 'wiki-versions',
                'content': home_wiki[1]
            })
            actions['updated'].append([nodeid, 'home', existingwikis[hometag]])
        del existingwikis[hometag]        
    else:
        resp = osf.osfpost(f'/nodes/{nodeid}/wikis/', {
                'type': 'wikis',
                'content': home_wiki[1],
                'name': 'home',
            }) 
        actions['created'].append([nodeid, 'home', resp['data']['id']])

    # Go through the rest of the wikis / sections
    for wikiname, text in wikis:        
        if wikiname in existingwikis:
            osf.osfpost(f'/wikis/{existingwikis[wikiname]}/versions/', {
                'type': 'wiki-versions',
                'content': text
            })  
            actions['updated'].append([nodeid, wikiname, existingwikis[wikiname]])
            del existingwikis[wikiname]
        else:
            # new wiki
            resp = osf.osfpost(f'/nodes/{nodeid}/wikis/', {
                'type': 'wikis',
                'content': text,
                'name': wikiname,
            }) 
            actions['created'].append([nodeid, wikiname, resp['data']['id']])

    # - now clear out any old wikis 
    #if deleteold and existingwikis:
    for wikiname, wikiid in existingwikis.items():
        osf.osfdelete(f'/wikis/{wikiid}/')
        actions['deleted'].append([nodeid, wikiname, wikiid])
    return(actions)
