# OSF Plugins from the URE Project

This repo contains all of the files to run the plugins developed to support the URE community interacting with OSF in more typical approaches.

## Organization

The repo functions both as a fully functional python flask environment and also as a codebase to accomplish the plugin tasks in a standalone context. This should allow for easier incorporation into the OSF codebase, if desired.  

The flask webserver is set up to run from the root of the `python` directory, allowing the custom built python modules to be imported without being installed, which also should help in testing and development.

Otherwise, here is a description of the folder layout:
* `bin/`: Executable files to start a development flask server and to get the metadata from the collection for the better search features
* `conf/`: Holds yaml files with account-specific information and API keys - see the credentials section below.

## Credentials

OSF and Google require developers to register their application in order to access their programmatic APIs, and so the credentials are stored in specific files in the `conf/` directory. You will need to set up the developer accounts and keys on your own.

### OSF Credentials

Register your application in **Developer Apps** for [OSF Production](https://osf.io/settings/applications)

## Set up Virtual Env

### Install the virtual-env package

```bash
sudo apt install python3-venv
```

From the root directory of the repo, run:

```bash
python -m venv osfvenv
source osfvenv/bin/activate
pip install -r requirements.txt
pip install pkg/mistune-package/
pip install pkg/osf-package
pip install pkg/ure-package
```

## License

All code is licensed under the GNU License, v 3.0, and requires attribution to the original author, [Kevin Crouse](https://gitlab.com/krcrouse), if used or incorporated into other products. Further, any products incorporating this code must be open source. A full copy of the GNU License is availabe in the root directory of the repository.