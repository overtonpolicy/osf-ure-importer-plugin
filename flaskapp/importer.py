import flask
import string, random
import re
import urllib.parse
import html
import sys

# get the local osf requests library
from . import osf
# Our webserver-unaware packages for processing things
import ure

UPLOADDIR = 'tmpfiles'
bp = flask.Blueprint('import', __name__, url_prefix='/import')

def standardized_decode(text):
    """ Fully unescape any text.
    
    We have found instances in which a string is html-escaped and then is url-encoded, leading to weird outcomes that aren't necessary clear from looking at the interface. So we get around this by decoding every option for wiki and component titles and then reencoding them as necessary """
    return(html.unescape(urllib.parse.unquote_plus(text)))

def standardized_encode(text):
    """ Return uri-encoded text for an arbitrary string. This function exists in case we need to manually improve the encoding in the future. """
    return(urllib.parse.quote(text))


@bp.route('/googledoc', methods=('GET', 'POST'))
def googledoc():
    """ The endpoint for the Google Document importer. If a GET request, returns the web form. POST is expected to be an ajax call to submit the import."""
    if flask.request.method == 'POST':
        return(googledoc_import())
    else:
        return(flask.render_template('import/googledoc.html'))


@bp.route('/docx', methods=('GET', 'POST'))
def docx():
    """ The endpoint for the MS Word Document importer. If a GET request, returns the web form. POST is expected to be an ajax call to submit the import."""
    if flask.request.method == 'POST':
        return(docx_import())
    else:
        return(flask.render_template('import/docx.html'))


@bp.route('/process_docx_upload', methods=['POST'])
def process_docx_upload():
    """ An endpoint to upload a docx file. The file will be written to the UPLOADDIR path with a generic random name. If the file does not have a docx extension it will be rejected - but this is unexpected behavior because the legitimate form also validates the extension pre-submission. 
    
    Returns: json dict of ('filename': the original filename, 'id': the new filename). 
    """
    docx = flask.request.files['upload-docx']
    
    if not re.search(r'\.docx$', docx.filename, re.I):
        raise Exception("Must upload a Microsoft Word Document File")

    # -- generate a filename
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + '.docx'
    
    docx.save(UPLOADDIR + '/' + filename)
    return({
        'filename': docx.filename, 
        'id': filename, 
    })

def docx_import():
    """ Import a MS Word Document.

    'rootnodeid': projectid,
        'rootnodename': projectname,
        'nodemap': nodelookup,
        'wikiactions': wikiactions,
        'componentactions': componentactions,
    """

    parameters = osf.parse_parameters(checkbox_params=['overwrite', 'deleteold']) 

    if 'fileid' not in parameters or not parameters['fileid']:
        raise Exception(f"You you upload a file to import. Please report this to tech support.")

    importer = ure.exporter.from_file(
        UPLOADDIR + '/' + parameters['fileid'], 
        section_break=parameters['section-break-policy'],
        page_break=parameters['page-break-policy'],
        h1_break=parameters['h1-policy'],
        h2_break=parameters['h2-policy'],        
    )
    return(render_import(importer, parameters))


def render_import(importer, parameters):
    """ The generic importer.
    
    Args:
        importer (ure.importer): An importer object that has already processed the source and is ready for actual import.
        parameters (dict): A standardized dict of params. 'overwrite' and 'deleteold' must be included.
    
    Returns (dict): 
        {
            'rootnodeid': The Project ID of the root node that was imported into,
            'rootnodename': The name of the root node that was imported into,
            'nodemap' (dict): A map of the node id to the node name for every node that was touched,
            'wikiactions' (dict(list(list))): the aggregate dict of the actions performed on wikis. The keys are ('created', 'updated', 'deleted', 'ignored') and each maps to a list of lists (node_id, wiki_name, wiki_id)
            'componentactions' (dict(list(list))): the aggregate dict of the actions performed on nodes/components. The keys are ('created', 'updated', 'deleted', 'ignored') and each maps to a list of lists (node_id, node_name, optionally an extra status message to be displayed to the user). The optional message does not exist in default/successful actions.
        }

    """

    if 'osf-project-id' not in parameters or not parameters['osf-project-id']:
        raise Exception(f"Required parameter osf-project-id not defined in form submission. Please report this to tech support.")

    projectid = parameters['osf-project-id']
    projectname = standardized_decode(parameters['osf-project-name'])

    overwrite = parameters['overwrite']
    deleteold = parameters['deleteold']

    # Nodelookup is a mapping of node id -> name for all nodes
    nodelookup = {projectid: projectname}

    # Verify that we are logged in
    ping = osf.getme(refresh=True)
    if ping['errors']:
        return(ping)

    # Get the existing subcomponents
    childjs = osf.osfgetdata(f"/nodes/{projectid}/children/", fetch_all=True)
    existingnodes = {}
    for jswiki in childjs:
        true_text = standardized_decode(jswiki['attributes']['title'])
        existingnodes[true_text] = jswiki['id']
        nodelookup[jswiki['id']] = true_text

    allcomponents = importer.markdown    
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
        component_name = standardized_decode(component_name)
        if component_name in existingnodes:
            newactions = render_wikis(existingnodes[component_name], compwikis, overwrite=overwrite, deleteold=deleteold)
            for k,v in newactions.items():
                wikiactions[k].extend(v)
            if newactions['created'] or newactions['updated'] or newactions['deleted']:
                componentactions['updated'].append([ existingnodes[component_name], component_name])
            else:
                componentactions['ignored'].append([ existingnodes[component_name], component_name])

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
                
                result = osf.osfdelete(f'/nodes/{nodeid}/', quiet=True)
                if result['errors']:
                    # Deleting nodes is complicated and can fail for more reasons
                    # than we are willing to capture - so if that's the only 
                    # problem we have, we list it for the user to fix.
                    componentactions['ignored'].append([nodeid, nodename, "Could not delete. Please do so manually."])
                else:
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
    """ Uses the osf module interface to create/update/delete the wiki pages for a single component. 
    
    Args:
        nodeid (str): The node whose wikis we are rendering
        wikis (list(tuple)): A list of 2-element tuples (wiki_name, wiki_content) that represents all the wikis to be set for this node.
        overwrite (bool): If True, whether to overwrite existing wikis. Default is True.
        deleteold (bool): If True, delete any existing wikis that are not updated. Default is False. 
    Returns dict(list): dict of actions performed with keys ('created', 'updated', 'deleted', ignored)
    """
    actions = {'created': [], 'updated': [], 'deleted': [], 'ignored': [] }

    wikijs = osf.osfgetdata(f"/nodes/{nodeid}/wikis/", fetch_all=True)
    existingwikis = {}
    for jswiki in wikijs:
        existingwikis[standardized_decode(jswiki['attributes']['name']).strip()] = jswiki['id']

    #
    # Handle the Home wiki
    #
    # It is possible for the home wiki not to exist as it is not automatically created when the component is created. However, as far as we can tell, if any wikis exist, the top one is home. 
    #
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
    else: # create new wiki
        resp = osf.osfpost(f'/nodes/{nodeid}/wikis/', {
                'type': 'wikis',
                'content': home_wiki[1],
                'name': 'home',
            }) 
        actions['created'].append([nodeid, 'home', resp['data']['id']])

    #
    # Go through the rest of the wikis / sections
    #
    for wikiname, text in wikis:   
        wikiname = standardized_decode(wikiname)     
        if wikiname in existingwikis:
            # wiki exists - update it if we can overwrite, else ignore
            if not overwrite:
                actions['ignored'].append([nodeid, wikiname, existingwikis[wikiname]])
            else:
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

    #
    # - Handle any existing wikis that were not updated - either delete or list as ignored
    #
    if deleteold:
        for wikiname, wikiid in existingwikis.items():
            osf.osfdelete(f'/wikis/{wikiid}/')
            actions['deleted'].append([nodeid, wikiname, wikiid])
    else:
        for wikiname, wikiid in existingwikis.items():
            actions['ignored'].append([nodeid, wikiname, wikiid])

    return(actions)
