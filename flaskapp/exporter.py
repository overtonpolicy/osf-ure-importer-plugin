import flask
import string, random
import re
import urllib.parse
import html
import sys

# get the local osf requests library
from . import osf

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
    parameters = osf.parse_parameters(checkbox_params=['include-components', 'add-titles']) 
    fmt = parameters['export-format']
    if fmt not in ('odt', 'docx', 'md'):
        raise Exception(f"Unknown export format '{fmt}'") 

    mkd = get_project_markdown(
        parameters['osf-project-id'],
        parameters['osf-project-name'],
        include_components=parameters['include-components'],
        add_titles = parameters['add-titles'],
        wiki_break = parameters['wiki-break-policy'],
        component_break = parameters['component-break-policy'],
    )
    print("All markdown:", mkd)
    return({'markdown': mkd})


def get_project_markdown(projectid, projectname, include_components, add_titles, wiki_break, component_break):

    markdown = ""
    # -- now get all the wikis 
    all_wikis = osf.osfgetdata(f"/nodes/{projectid}/wikis/", fetch_all=True)
    home = all_wikis.pop(0)
    
    # -- handle the home wiki. If add_titles is true, this should be the node title, not the wiki title
    if add_titles:
        markdown += "# " + projectname + "\n"
    
    content = osf.osfapicall(home['links']['download'], return_json=False)
    markdown += content + "\n"

    for wiki in all_wikis:
        wiki_title = wiki['attributes']['name']
        
        # download the content
        content = osf.osfapicall(wiki['links']['download'], return_json=False)
        print(f"Wiki title (nostderr) " + wiki_title)
        print(f"Wiki '{wiki_title}' download link: {wiki['links']['download']}", file=sys.stderr)
        if wiki_break == 'page':
            markdown += "%%%%%%"
        elif wiki_break == 'section':
            markdown += "&&&&&&"
        if add_titles:
            markdown += "\n# " + wiki_title + "\n" + content + "\n"
        else:
            markdown += "\n" + content + "\n"

    if include_components:
        children = osf.osfgetdata(f"/nodes/{projectid}/children/", fetch_all=True)
        for child in children:
            if component_break == 'page':
                markdown += "%%%%%%"
            elif component_break == 'section':
                markdown += "&&&&&&"
            markdown += "\n" + get_project_markdown(child['id'], child['attributes']['title'], include_components, add_titles, wiki_break, component_break)
    return(html.unescape(markdown))
