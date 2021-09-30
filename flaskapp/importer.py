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
    return(flask.render_template('import/docx.html'))


@bp.route('/process_docx_upload', methods=['POST'])
def process_docx_upload():
    if flask.request.method == 'POST':
        print("POSTING!")
    else:
        print("GETTING")
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
    return({'errors': [{'detail': 'Still finishing up the logic'}]})


    parameters = {k:None if v == '' else v for k,v in flask.request.form.items()}

    for reqparam in ['osf-project-id', 'fileid']:
        if not parameters[reqparam]:
            pass
            #raise Exception(f"Required parameter {reqparam} not defined in form submission. Please report this to tech support.")

    exporter = ure.exporter.from_file(
        uploaddir + '/' + parameters['fileid'], 
        section_break=parameters['section-break-policy'],
        page_break=parameters['page-break-policy'],
        h1_break=parameters['h1-policy'],
        h2_break=parameters['h2-policy'],        
    )

    nodeid = parameters['osf-project-id']
    prjname = parameters['osf-project-name']

    overwrite = parameters['overwrite']
    clear_unused = False
    childjs = osf.osfgetdata(f"/nodes/{nodeid}/children/", fetch_all=True)
    wikijs = osf.osfgetdata(f"/nodes/{nodeid}/wikis/", fetch_all=True)
    '''
    existingwikis = {}
    existingnodes = {}
    for jswiki in childjs:
        existingnodes[jswiki['attributes']['title']] = jswiki['id']
    for jswiki in wikijs:
        existingwikis[jswiki['attributes']['name']] = jswiki['id']
    
    #layout = ''
    actions = {
        'updated': [],
        'created': [],
        'deleted': [],
    }
    compwikis = exporter.markdown    
    root_project = compwikis.pop(0)    
    layout += '<h1>Root Project: ' + root_project[0] + '</h1>'
    wikis = root_project[1]


    def render_wikis()
    home_wiki = wikis.pop(0)
    if existingwikis:
        hometag = 'home' if 'home' in existingwikis else 'Home'
        if hometag not in existingwikis:
            raise Exception(f"Cannot identify the home wiki. Wiki names are: '" + "','".join(existingwikis) + "'")
        # post updated content to the wiki
        osf.post(f'/wikis/{existingwikis[hometag]}/versions/', data={
            'type': 'wiki-versions',
            'content': home_wiki[1]
        })
        actions['updated'].append(f"Set the home wiki for {prjname}")
        del existingwikis[hometag]        
    else:
        raise Exception("We could not identify any existing wiki for this project. Is that possible? Contact kevin with this example.")

    for wikiname, text in wikis:        
        #layout += '<h2>Root Wiki: ' + wiki + '</h2><p>' + text + '</p>'
        if wikiname in existingwikis:
            # post updated content to the wiki
            osf.post(f'/wikis/{existingwikis[wikiname]}/versions/', data={
                'type': 'wiki-versions',
                'content': text
            })  
            actions['updated'].append(f"Updated the {wikiname} wiki for {prjname}")
            del existingwikis[wikiname]
        else:
            # new wiki
            osf.post(f'/nodes/{nodeid}/wikis/', data={
                'type': 'wikis',
                'content': text,
                'name': wikiname,
            }) 
            actions['created'].append(f"Created a new wiki, '{wikiname}', for {prjname}")

    # - now clear out any old wikis 
    #if clear_unused and existingwikis:
    #    for wikiid in existingwikis.values():
    #        osf.delete()


    for component_name, allwikis in compwikis:
        
        homewiki = allwikis.pop(0)

        
        #layout += '<h1>Component: ' + comp[0] + '</h1>'
        #for wiki, text in comp[1]:
        #    layout += '<h2>Wiki: ' + wiki + '</h2><p>' + text + '</p>'

    #import pprint
    #ppjs = pprint.pformat(js, indent=4)
    return(f"""<html>
    <body>
    <h1>SOMETHING HAPPENED</h1>
    <h2>Params</h2>
    {parameters}    
    <h1>Existing Wikis</h1>
    {existingwikis}
    <h1>Existing Wikis</h1>
    {existingnodes}
    <h1>Layout</h1>
    <pre>
    {layout}
    </pre>
    <a href="{flask.url_for('import.docx')}">Return to form</a>
    <h1>OSF RAW</h1>
    <pre>
    </pre>
    </body></html>""")
    '''