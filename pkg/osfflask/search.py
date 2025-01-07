"""
Copyright (c) 2024, Kevin Crouse. 

This file is part of the *URE Methods Plugin Repository*, located at 
https://github.com/kcphila/osf-ure-plugins

This file is distributed under the terms of the GNU General Public License 3.0
and can be used, shared, or modified provided you attribute the original work 
to the original author, Kevin Crouse.

See the README.md in the root of the project directory, or go to 
http://www.gnu.org/licenses/gpl-3.0.html for license details.
"""

import flask
import string, random
import urllib.parse
import html
import tempfile
import os, sys, re
import json 
import duckdb

# get the local osf requests library
from . import osf
import ure.exporter

bp = flask.Blueprint('search', __name__, url_prefix='/search')

@bp.route('/advanced')
def advancedsearch():
    return(flask.render_template('advancedsearch.html'))

@bp.route('/conduct_search', methods=('POST',))
def run_search():
    """ Run the search ."""
    parameters = osf.parse_parameters() 

    if 'searchtext' not in parameters or not parameters['searchtext']:
        raise Exception(f"You must provide some text to search by.")

    if not re.search(r'\w{3}', parameters['searchtext']):
        raise Exception("You must search for at least one word!")

    words = ['%' + word + '%' for word in re.split(r'\s+', parameters['searchtext'].lower())]
    script_dir = os.path.dirname(os.path.realpath(__file__))
    print(f"Attempting to open {script_dir + '/../../data/collectiondb.duckdb'}") 
    dbh = duckdb.connect(database=script_dir + '/../../data/collectiondb.duckdb', read_only=True)
    sth = dbh.cursor()
    sth.execute("select project, authors, url from node_text where " + " AND ".join(["text like ?" for i in words]), words)
    
    #organize
    results = [] 
    for prj, authors, url in sth.fetchall():
        results.append([  
            f'<a href="{url}" target="_blank"><div class="article-title">{prj}</div></a>', 
            authors,
        ])

    dbh.close()
    
    return({'success':True, 'results': results})

