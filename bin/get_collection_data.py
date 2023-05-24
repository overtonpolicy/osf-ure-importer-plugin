#!/usr/bin/python3
import sys,os,re
import shutil
import traceback,pdb
import urllib
from pprint import pprint
import json
import tempfile
import duckdb

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', action='store_true', help='print things')
args = parser.parse_args()

import osf


with open('conf/osf.pat') as fh:
    token = fh.read().strip()

def main():
    try:
        do_stuff()
    except Exception as e:
        if args.debug:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
        raise


def do_stuff():
    """ 
    create the total collection data structure:
    collection_data is an array of {
        'id',
        'url',
        'title', 
        'description',
        'subjects': [], 
        'tags': [], 
        'wikis': list of {
            'name',
            'url',
            'text',
            'date_modified',
        }
        'contributors': list of {
            'name',
            'id',
            'url',
        },
        'collected_type',
        'program_area',
        'date_created', 
        'date_modified', 
        'public', 
        'wiki_enabled',

    }
    """
    session = osf.session(token)

    #
    # This gets all of the nodes in the collection.
    # TODO: this will need to be incremental at some point when re-fetching all data 
    # every day is inefficient and not sustainable.
    #

    collection_nodes = session.get_all('/search/collections/', params={
        'q':"id:(ux3nq)",
    })

    if len(collection_nodes) == 0:
        raise Exception("FAILED TO FETCH ANY COLLECTION NODES")

    nodeinfo = {}
    for js in collection_nodes:
        gudata = js['embeds']['guid']['data']
        
        if js['attributes']['program_area'] == 'N/A':
            program_area = None
        else:
            program_area = js['attributes']['program_area']

        if js['attributes']['collected_type'] == 'N/A':
            collected_type = None
        else:
            collected_type = js['attributes']['collected_type']


        nodeinfo[gudata['id']] = {
            'collected_type': collected_type,
            'program_area': program_area,
        }        
    
    #
    # This now fetches all of the linked nodes in the collection, which is necessary to fetch author/bibliographic data (which isn't contained in the /search/collections endpoint). 
    # TODO: As with the prior fetch, this has a shelf life because it's not sustainable to re-fetch all data in the collection every day.
    #

    nodes = session.get_all('/collections/ux3nq/linked_nodes/', params={
        'embed': ['bibliographic_contributors', 'wikis',],
    })

    #
    # Here we combine the data collected in the two prior fetches to create a single data structure, and then download wiki content as appropriate.
    #
    collection_data = []
    for nodejs in nodes:

        # the node object is what we are going to store persistently. The ID and URL are key.
        node = {
            'id': nodejs['id'],
            'url': nodejs['links']['html'],
        }
        
        # then there are attributes
        for key in ('date_created', 'date_modified', 'description', 'public', 'subjects', 'tags', 'title', 'wiki_enabled'):
            node[key] = nodejs['attributes'][key] 

        # add in the information from the collection search and move it into the full data structure
        if nodejs['id'] in nodeinfo:
            node.update(nodeinfo[nodejs['id']])
        else:
            for key in ('collected_type', 'program_area',):
                node.setdefault(key, None)

        # now the author data
        node['contributors'] = []
        for contrib in nodejs['embeds']['bibliographic_contributors']['data']:
            if 'data' in contrib['embeds']['users']: 
                user = contrib['embeds']['users']['data']
                full_name = user['attributes']['full_name']
                node['contributors'].append({
                    'name': full_name,
                    'id': user['id'],
                    'url': user['links']['html'],
                }) 
            elif 'errors' in contrib['embeds']['users']:
                # This happens when the user account has been deactivated
                err = contrib['embeds']['users']['errors'][0]
                if 'meta' in err and 'full_name' in err['meta']:
                    node['contributors'].append({
                        'name': err['meta']['full_name'],
                        'id': -1,
                        'url': None,
                    })

        # here we fetch the wiki information 
        node['wikis'] = []
        for wikiref in nodejs['embeds']['wikis']['data']:
            wiki = {
                'name': wikiref['attributes']['name'],
                'date_modified': wikiref['attributes']['date_modified'],
                'url': 'https://osf.io' + wikiref['attributes']['path'], # this is odd, but true
            }
            text_url = wikiref['links']['download']
            wikidata = session.get(text_url)
            wiki['text'] = wikidata.text
            node['wikis'].append(wiki)
        collection_data.append(node)

    if args.debug:
        pprint(collection_data, width=200)

    load_duckdb(collection_data)

    with open('data/collectioninfo.json', 'w') as fh:
        json.dump(collection_data, fh)    

def load_duckdb(collection_data):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.duckdb')
    tfpath = tf.name
    os.remove(tfpath)
    dbh = duckdb.connect(database=tfpath, read_only=False)
    sth = dbh.cursor()
    sth.execute('create table node_text(id integer NOT NULL PRIMARY KEY, project varchar NOT NULL, authors varchar NOT NULL, url varchar NOT NULL, text varchar NOT NULL)')
    sth.execute('create sequence pk_nodetext start 10001')

    for prj in collection_data:
        inserts = []

        textpieces = []
        for field in ('title', 'description', 'program_area', 'collected_type'):
            if prj[field]:
                textpieces.append( prj[field] )

        if 'tags' in prj and prj['tags']:
            textpieces.extend(prj['tags'])

        for wiki in prj['wikis']:
            if wiki['text']:
                textpieces.append( wiki['text'] )

        inserts.append([  wiki['text'] ])
        
        sth.execute("insert into node_text(id, project, authors, url, text) values (nextval('pk_nodetext'), ?, ?, ?, ?)", [
            prj['title'], 
            '; '.join([contrib['name'] for contrib in prj['contributors']]),
            prj['url'],
            ' '.join([t.lower() for t in textpieces])
        ])
    dbh.close()
    shutil.copy(tfpath, 'data/collectiondb.duckdb')


if not args.debug:
    main()
else:
    try:
        main()
    except:
        errtype,errvalue,errtb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(errtb)

