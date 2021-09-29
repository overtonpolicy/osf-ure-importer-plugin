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

    js = osf.osfget(f"/nodes/{parameters['osf-project-id']}/", {'embed': ['wikis', 'children']})
    existingwikis = {}
    existingnodes = {}
    for jswiki in js['embeds']['wikis']:
        existingwikis[jswiki['attributes']['name']] = jswiki['id']
    for jswiki in js['embeds']['children']:
        existingnodes[jswiki['attributes']['title']] = jswiki['id']

    layout = ''
    compwikis = exporter.markdown    
    root_project = compwikis.pop(0)
    layout += '<h1>Root Project: ' + root_project[0] + '</h1>'
    for wiki, text in root_project[1]:
        layout += '<h2>Root Wiki: ' + wiki + '</h2><p>' + text + '</p>'

    for comp in compwikis:
        layout += '<h1>Component: ' + comp[0] + '</h1>'
        for wiki, text in comp[1]:
            layout += '<h2>Wiki: ' + wiki + '</h2><p>' + text + '</p>'

    return(f"""<html>
    <body>
    <h1>SOMETHING HAPPENED</h1>
    <h2>Params</h2>
    {parameters}
    <h1>Existing Wikis</h1>
    {existingwikis}
    <h1>Layout</h1>
    <pre>
    {layout}
    </pre>
    <a href="{flask.url_for('import.docx')}">Return to form</a>
    </body></html>""")
