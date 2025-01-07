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


from .baseclass import BaseImporter
from .docx import DocX
import re 

def from_file(filename, **kwargs):
    """ Identify the correct class from the file extension and return an object of it.
    
    Args:
        filename: The path the file to load.
        kwargs: Other parameters that will be passed to the constructor of the sublcass.
    Returns:
        An instantiated object of the appropriate type.

    """
    if re.search(r'\.docx$', filename, re.I):
        return DocX(filename, **kwargs)
    else:
        raise Exception(f"Cannot identify a parsable file extension from {filename}")