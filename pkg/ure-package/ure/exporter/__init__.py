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

class BaseExporter():
    """Exporter baseclass to standardized options."""
    def __init__(
            self, 
            include_components:bool=True, 
            wiki_break_type:str=None, 
            component_break_type:str='page', 
            auto_titles:bool=True, 
            add_component_titles:bool=False, 
            add_wiki_titles:bool=False,
            debug:bool=False,
    ):
        self.auto_titles = auto_titles
        self.add_component_titles = add_component_titles        
        self.add_wiki_titles = add_wiki_titles        
        self.include_components = include_components
        self.wiki_break_type = wiki_break_type
        self.component_break_type = component_break_type
        self.debug=debug

    def process_markdown(self, markdown:str):
        raise NotImplementedError(
            "process_source must be defined in the subclass to return a ure-markdown datastructure"
        )

from .docx import Docx