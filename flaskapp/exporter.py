import flask
import string, random
import re
import urllib.parse
import html
import sys
import tempfile

# get the local osf requests library
from . import osf
import ure.exporter

bp = flask.Blueprint('export', __name__, url_prefix='/export')


@bp.route('/file', methods=('GET', 'POST'))
def export_to_file():
    """ The endpoint for the document exporter. If a GET request, returns the web form. POST is expected to be an ajax call to submit the import."""
    if flask.request.method == 'POST':
        return(file_export())
    else:
        return(flask.render_template('export/to_file.html'))

def file_export():
    """ Export a project to a file.
    """
    #
    # render parameters 
    #
    parameters = osf.parse_parameters(checkbox_params=['include-components', 'add-wiki-titles', 'add-component-titles']) 
    fmt = parameters['export-format']
    if fmt not in ('odt', 'docx', 'md'):
        raise Exception(f"Unknown export format '{fmt}'") 

    mkd = get_project_markdown(
        parameters['osf-project-id'],
        parameters['osf-project-name'],
        include_components=parameters['include-components'],
    )

    exporter = ure.exporter.Docx(
        style_template="conf/APA Double Space.docx",
        add_component_titles=parameters['add-component-titles'],
        add_wiki_titles=parameters['add-wiki-titles'],
        wiki_break_type=parameters['wiki-break-policy'],
        component_break_type=parameters['component-break-policy'],
    )
    doc = exporter.process_markdown(
        mkd,
    )
    filename = re.sub(r'[^\s\w]', '', mkd[0][0]) + '.' + fmt
    with tempfile.NamedTemporaryFile(suffix="." + fmt) as fh:
        doc.save(fh.name)
        doc.save("/tmp/tmp.docx")
        fh.flush()
        fh.seek(0)
    return(flask.send_file("/tmp/tmp.docx", 
            as_attachment=True, 
            download_name=filename,
            attachment_filename=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ))  
    #return(flask.send_file("../tmp.docx", as_attachment=False, download_name=filename))        

def get_project_markdown(projectid, projectname, include_components):
    """
    Returns:
        [
            (<Project Name>, [
                [<Project Name>, <home wiki content>],
                [<Wiki 2 name>, <Wiki 2 content>], 
                ...
            ]),
            (<Component Name>, [
                [<Component Name>, <home wiki content>],
                [<Wiki 2 name>, <Wiki 2 content>], 
                ...
            ]),
            (<Component 2 Name>, [
                [<Component 2 Name>, <home wiki content>],
                [<Wiki 2 name>, <Wiki 2 content>], 
                ...
            ]),
        ]
    Notes:
        The top-level project, components, and any nested subcomponents all will appear at the same level. There is no nesting of components in return
    """
    content = []

    # -- now get all the wikis 
    all_wikis = osf.osfgetdata(f"/nodes/{projectid}/wikis/", fetch_all=True)
    
    project_wikis = []
    # -- handle the home wiki. If add_titles is true, this should be the node title, not the wiki title
    home = all_wikis.pop(0)
    homecontent = osf.osfapicall(home['links']['download'], return_json=False)
    project_wikis.append([projectname, html.unescape(homecontent)])

    for wiki in all_wikis:
        wiki_title = wiki['attributes']['name']        
        wikicontent = osf.osfapicall(wiki['links']['download'], return_json=False)
        project_wikis.append([wiki_title, html.unescape(wikicontent)])

    content.append( (projectname, project_wikis) )

    if include_components:
        subcomponents = osf.osfgetdata(f"/nodes/{projectid}/children/", fetch_all=True)
        for component in subcomponents:
            subcontent = get_project_markdown(
                component['id'],
                component['attributes']['title'], 
                include_components, 
            )
            content.extend(subcontent)
    return(content)


    md = [
        ['Main Project', [
            ['Wiki', text],
        ]],
    ]

