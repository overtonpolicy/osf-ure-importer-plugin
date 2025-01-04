# OSF Plugins from the URE Project

This repo contains all of the files to run the plugins developed to support the URE community interacting with OSF in more typical approaches.

# Key Notes

- When testing, it is important to note that `http://127.0.0.1` and `http://localhost` are not the same. The current code works against `http://localhost`. Entering `127.0.0.1` in the web browser may end up rendering the HTML correctly but not authenticating against OSF or Google.

# Overview

The repo functions both as a fully functional python flask environment and also as a codebase to accomplish the plugin tasks in a standalone context. This should allow for easier incorporation into the OSF codebase, if desired.  

The flask webserver is set up to run from the root of the `python` directory, allowing the custom built python modules to be imported without being installed, which also should help in testing and development.

Otherwise, here is a description of the folder layout:
* `bin/`: Executable files to start a development flask server and to get the metadata from the collection for the better search features
* `conf/`: Holds yaml files with account-specific information and API keys - see the credentials section below.

# Credentials

OSF and Google require developers to register their application in order to access their programmatic APIs, and so the credentials are stored in specific files in the `conf/` directory. You will need to set up the developer accounts and keys on your own.

## OSF Credentials

Register your application in **Developer Apps** for [OSF Production](https://osf.io/settings/applications)

# Set Up

This code is built on Python 3.10. It is highly recommended to use a python virtual environment 
for the repository.

## Package Installation

Custom, modified, and in-house packages are all in the `pkg/` folder, but are also referenced in `requirements.txt`


```bash
pip install -r requirements.txt
```

## Other Requirements

Additionally, these utilities are required:

- pandoc

# Cached Collection Information (`bin/get_collection_data.py`)

The OSF collection details are fetched and cached locally via the 
`bin/get_collection_data.py` script, and this is used for several of the front 
end tools. Having the tools hit OSF directly from the client is slow and leads 
to inconsistent results when OSF has network lags.

This saves both a json data file of details and a DuckDB database for advanced
querying.

After running `bin/get_collection_data.py`, the cached files are stored in `data/`
and a copy of the json dump is also stored in the static web repository.

# Running the Local Server (`bin/startflask`)

Running `bin/startflask` will start the local flask server that includes the various plugins and add-ons.
After the server starts up, navigate to http://127.0.0.1:3000/

## Most Recent OSF Collection Items Table

The [Most Recent Collection Items](http://localhost:3000/collectionlist) uses 
jquery (and jquery-table) to create a more interactive, searchable 
table of URE Sources in the collection. This uses the JSON OSF cache file
pulled down by `get_collection_data.py`

## Advanced Search

The [Advanced Search](http://localhost:3000/search/advanced) uses 
jquery (and jquery-table) to create an interactive search that includes content 
from wiki pages as well as different fields. At the time of development, this 
was both faster and included more features than the OSF search. This uses the 
DuckDB database constructed from OSF sources pulled down by `get_collection_data.py`

# Exporter


# Importer

## Word Importer


## Google Drive/Docs Importer

The Google Docs Importer uses, as expected, Google Docs.


# License

All code is licensed under the GNU License, v 3.0, and requires attribution to the original author, [Kevin Crouse](https://gitlab.com/krcrouse), if used or incorporated into other products. Further, any products incorporating this code must be open source. A full copy of the GNU License is availabe in the root directory of the repository.