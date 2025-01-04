# Running and Developing OSF-URE Tools

This document  provides details about the tools, features, and existing codebase. 
It provides more guidance for active development and how to run a local 
development server for ongoing work.

In constrast, the [SETUP.md](SETUP.md) describes the procedures for initial set 
up and configuration.

The [README.md](README.md) provides an overview of the project.

# Design and Terminology

## Terminology 

The OSF platform is very flexible, but there is a certain level of complexity
that comes with that flexibility. A **Project** is a core entity that can include
"Wikis" (pure-text documents that can be rendered with various types of 
formatting), data files, links, and lots of other stuff. 

OSF wikis are markdown-based (as is Wikipedia). 

A **Project** can includes sub-projects, which we designate as **Components**.
In OSF, each *Component* is also a full fledged *Project* with all of the tools 
and facets of a top-level project. This is exemplified in the 
[Reproducibility Projects](https://osf.io/ezcuj/wiki/home/) that essentially 
led to the creation of OSF. The *Reproducibility Project* is a parent project to 
each Component, which are single replications of prior studies. In this 
situation, the "Component" is a physical study that has little relation to the 
other "Components."  The "Component" may itself include sub-projects (which are 
then Components of Components).

When discussing document formats, the terminology will related to Microsoft Word,
though this primarily is similar to terminology in LibreOffice and other 
Word Processing platforms.

## Design Needs

One of the identified needs for the URE project was to provide tools so that 
everyday, nontechnical researchers can interact with their research in whatever
word processor they use, and in whatever stage of the research process they are 
in, and still engage with the OSF / URE platform.

Many less-technical researchers also do not take full advantage of their word 
processing platform (whether Libre Office, Microsoft Office, or something else),
and so it is also important to provide some options when building tools that 
convert between OSF and the related document platforms. 

I do not feel the initial URE project was very successful in succinctly 
conveying the feature options to such stakeholders in ways that were clear 
and not overwhelming, and so I leave it to you to figure that out!

# Runtime Notes

## URLs

When testing, it is important to note that `http://127.0.0.1` and 
`http://localhost` are not the same and that the OSF Developer app configuration
only allows `localhost` (as of the time of writing). Thus, current code works against 
`http://localhost`. Entering `127.0.0.1` in the web browser will end up 
rendering the HTML correctly but not authenticating against OSF.

The flask webserver and all scripts are designed to run from the root of repo
directory. Do not descend into subdirectories to run anything.

## Markdown

OSF uses Markdown for it's wikis, and there are many markdown "flavors" or 
"dialects." 

To maximize the translation between documents and OSF, adaptors have been added:
- Custom filters for `pandoc` calls are in `pkg/ure-package/ure/importer/pandoc/`
- `pkg/ure-package/ure/importer/docx.py` has a function `hack_docx`, which further manipulates the MS Word docx file for features that pandoc simply didn't have available.
- `pkg/ure-package/ure/importer/baseclass.py` has a `postprocess_markdown` function that translates the tokens added by `hack_docx` back into appropriate markdown
- The **mistune v2** python package is used by the exporter to (initially) translate the OSF Wiki markdown, but it's not complete, especially for the mathjax/equations supported by OSF. I have thus written a mathjax plugin for mistune to support this. I submitted a PR to the official mistune account, but it was rejected by the author, who was working on and since released mistune v3. At present, the forked mistune v2 package with my experimental plugin is in this repository and part of the requirements file

# Features

## Cached Collection Information (`bin/get_collection_data.py`)

The OSF collection details are fetched and cached locally via the 
`bin/get_collection_data.py` script, and this is used for several of the front 
end tools. Having the tools hit OSF directly from the client is slow and leads 
to inconsistent results when OSF has network lags.

This saves:
- A JSON data file of details for the sources in the URE Collection
- A [DuckDB](https://duckdb.org/) columnar database of source fields, used for advanced querying

After running `bin/get_collection_data.py`:
- The DuckDB Database is stored in `data/`
- The JSON data file is stored in `data/`
- The JSON data file is also stored in `pkg/osfflask/static/data/`, which is used by the local flask server

## Running the Local Server (`bin/startflask`)

Running `bin/startflask` will start the local flask server that includes the various plugins and add-ons.
After the server starts up, navigate to http://localhost:3000/

### Most Recent OSF Collection Items Table

The [Most Recent Collection Items](http://localhost:3000/collectionlist) uses 
jquery (and jquery-table) to create a more interactive, searchable 
table of URE Sources in the collection. This uses the JSON OSF cache file
pulled down by `get_collection_data.py`

### Advanced Search

The [Advanced Search](http://localhost:3000/search/advanced) uses 
jquery (and jquery-table) to create an interactive search that includes content 
from wiki pages as well as different fields. At the time of development, this 
was both faster and included more features than the OSF search. This uses the 
DuckDB database constructed from OSF sources pulled down by 
`get_collection_data.py`

### Exporter

The [OSF Exporter](http://localhost:3000/export/file) will take the wikis from 
an OSF Project and convert them into a word processor file.

There are plans to export to various formats, but currently only 
**Microsoft Word** and **Markdown Text** are supported. 

Wiki formatting is translated into the appropriate formatting for the export 
document type. Headings in the wikis will relate to the same Heading level 
in the exported document; when a wiki title is added as a heading, it will be 
added as a `Heading 1`.

By default, if the wiki content does not start with a heading, the wiki title 
will be added as a `Heading 1`. The wiki title will be ignored if there is 
a heading as the first line of the wiki content (by default).

Options for the Exporter:

- **Include Subcomponents** will descend into OSF Sub-projecst to export the details from them as well
- **Add Titles as necessary** adds the *Wiki Title* as a heading if the actual wiki data does not start with a `# Heading`. 
- **Always add *Component* titles** will always include the title of a OSF sub-project a heading, even if the the *Home* wiki for the component starts with a heading.
- **Always add Wiki titles** will always include the title of any wiki as a heading, even if the wiki content starts with a heading (in that case, both headings will appear in the export).
- **Break Between Wikis** specifies a type of document break when there are multiple wikis in an OSF project. The default is not to have any sort of break.
- **Break Between Components** specifies a type of document break when there are OSF sub-projects linked to the project being exported. The default is to have a page break.

### Importer

#### Word Importer

The [URE Microsoft Word Importer](http://localhost:3000/import/docx) imports a 
Microsoft Word file, obviously. You must be signed in to OSF as your personal 
user. You upload the file in the **Microsoft Word Document** section, select 
options that appeal to you, and run it.

Options for the Word docx importer:

- **Overwrite** indicates that existing wikis can be overwritten. If this not checked, any existing wiki will be ignored (and this is reported to the user).
- **Delete Old** will first delete any existing wikis for the project before importing new text.
- **Section Break Action** indicates how to interpret a **Section Break** in the source document. By default, a new Component (sub-project) will be created for this.
- **Page Break Action** indicates how to intepret a **Page Break** in the source document. By default, a new Component (sub-project) will be created for this.
- **Heading 1 Actions** indicates how to interpret top-level headings. By default, each top-level heading will lead to a new Wiki in the project.
- **Heading 2 Actions** indicates how to interpret second-level headings. By default, second-level headings do nothing special and will appear as Heading 2 within the wiki. 

#### Google Drive/Docs Importer

The [Google Docs Importer](http://localhost:3000/import/google) uses, as 
expected, Google Docs. You must be signed in to OSF as your personal 
user AND give Google permissions to the Drive and Document account for the user 
who is importing the document. 

With the *Google Doc Importer*, the user searches and selects the document to 
import from the Google Drive. They do not need to download it or export it in 
any way.

Options for the Google Docs Importer are similar to the Word docx importer:

- **Use Shared Drives** will search shared drives (instead of just primary user owned) when looking for documents.
- **Overwrite** indicates that existing wikis can be overwritten. If this not checked, any existing wiki will be ignored (and this is reported to the user).
- **Delete Old** will first delete any existing wikis for the project before importing new text.
- **Section Break Action** indicates how to interpret a **Section Break** in the source document. By default, a new Component (sub-project) will be created for this.
- **Page Break Action** indicates how to intepret a **Page Break** in the source document. By default, a new Component (sub-project) will be created for this.
- **Heading 1 Actions** indicates how to interpret top-level headings. By default, each top-level heading will lead to a new Wiki in the project.
- **Heading 2 Actions** indicates how to interpret second-level headings. By default, second-level headings do nothing special and will appear as Heading 2 within the wiki. 
