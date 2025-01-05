[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# OSF Plugins for the URE Project

This repo contains files and tools to run plugins developed by 
[Kevin Crouse](https://www.linkedin.com/in/kevincrouse/), Co-PI
of the [Use of Research Evidence (URE) Methods project](https://uremethods.org).

The URE Methods Project uses the [Open Science Framework (OSF)](https://osf.io), a 
free and open source software project to support collaborative research. The 
tools and resources in this repository interact with the OSF API.

# Orientation

Open Science is a fledgling, community enterprise. It is important and necessary 
if we want practitioners on the ground to actually be able to obtain and apply
research in practice, which is necessary to improve conditions for struggling 
memboers of our community and, by extension, for everyone else.

The OSF platform is a good starting point, but thus far it has been used 
primarily by tech-saavy, physical science researchers. Additional features are 
needed for social science (let alone humanities) researchers, and tools need
to be provided so that researchers who do not know "markdown" can also engage
with the platform. 

This repository attempts to provide tools and plugins to support these research
clients.

# Local Development and Runtime

The [SETUP.md](SETUP.md) document indicates the requirements to configure the 
repo for your own use. This is intended to be the initial configuration and setup
document and you likely do not need to reference it after initial setup.

The [RUNTIME.md](RUNTIME.md) document provides details about the tools, features,
and existing codebase. It provides more guidance for active development.

## Running the Server

If you have already configured everything:

Refresh the local cache of URE Collection documents:

```sh
bin/get_collection_data.py
```

Run the server:

```sh
bin/startflask
```

# About the URE Methods Project

# About OSF

[OSF](https://osf.io) is a project and platform developed by the 
[Center for Open Science (COS)](https://www.cos.io/). 

> The Center for Open Science (COS) was founded in 2013 to 
> start, scale, and sustain open research practices that will democratize access to 
> research, improve inclusion of all stakeholders, enhance accountability to research 
> integrity, facilitate the self-corrective process of science, expand transparency
> and sharing of all research content, and improve research rigor and reproducibility"
> ([COS](https://www.cos.io/about)). 

The URE Methods team has no formal affiliation with COS or OSF, but they're good
people doing good things.

# Authors

- [Kevin Crouse](mailto:krcrouse@gmail.com), original author. 

# License

External projects included in this repo retain their original license and 
attribution, and the mistune package (located in `pkg/mistune-package`) is a 
fork of an external package and licensed under the same (BSD) license. See 
relevant license details in the respective subdirectories.

Otherwise, all code is licensed under the 
[GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html#license-text), 
which requires attribution to the original author, 
[Kevin Crouse](https://github.com/kcphila), if used or incorporated into other 
products. Further, any products incorporating this code must be open source. A 
full copy of the [GPL](LICENSE) is availabe in the root directory of 
the repository.

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full text of the GNU General Public License should be in the root directory 
of this product. If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.
