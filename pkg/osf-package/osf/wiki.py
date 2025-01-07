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

from . import OSFBase

class Wiki(OSFBase):
    """A python class to represent an OSF Project Wiki
    """

    json_properties = ['attributes', 'id', 'links', 'relationships', 'type']

    def __init__(self, jref, session):
        self.session = session
        self.process_json(jref)

    @property
    def date_modified(self):
        return(self.json['attributes']['date_modified'])

    @property
    def kind(self) -> str:
        return(self.json['attributes']['kind'])        

    @property
    def name(self) -> str:
        if 'name' in self.json['attributes']: 
            return(self.json['attributes']['name'])


    @property
    def extra(self) -> str:
        return(self.json['attributes']['extra'])


    @property
    def content_type(self) -> str:
        return(self.json['attributes']['content_type'])


    @property
    def path(self) -> str:
        return(self.json['attributes']['path'])

    @property
    def current_user_can_comment(self) -> bool:
        return(self.json['attributes']['current_user_can_comment'])

    @property
    def materialized_path(self) -> str:
        return(self.json['attributes']['materialized_path'])

    @property
    def size(self) -> int:
        return(self.json['attributes']['size'])

