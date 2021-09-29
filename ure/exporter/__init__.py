from .baseclass import BaseExporter
from .docx import DocX

import re 
def from_file(filename, **kwargs):
    if re.search(r'\.docx$', filename, re.I):
        return DocX(filename, **kwargs)
    else:
        raise Exception(f"Cannot identify a parsable file extension from {filename}")