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