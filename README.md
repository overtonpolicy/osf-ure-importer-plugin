# OSF Plugins for the URE Project

This repo contains files and tools to run plugins developed by 
[Kevin Crouse](https://www.linkedin.com/in/kevincrouse/), Co-PI
of the [Use of Research Evidence (URE) Methods project](https://uremethods.org).

The URE Methods Project uses [Open Science Framework (OSF)](https://osf.io), a 
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

# Overview

The repo functions both as a fully functional python flask environment and also
as a codebase to accomplish the plugin tasks in a standalone context. This 
should allow for easier incorporation into the OSF codebase, if desired.  

Otherwise, here is a description of the folder layout:
* `bin/`: Executable files to start a development flask server and to get the metadata from the collection for the better search features
* `conf/`: Holds yaml files with account-specific information and API keys - see the credentials section below.

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

# License

All code is licensed under the GNU License v3, and requires attribution to 
the original author, [Kevin Crouse](https://github.com/kcphila), if used or 
incorporated into other products. Further, any products incorporating this code 
must be open source. A full copy of the [GPL](LICENSE) is availabe in the root 
directory of the repository.

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full text of the GNU General Public License should be in the root directory 
of this product. If not, see <https://www.gnu.org/licenses/>.
