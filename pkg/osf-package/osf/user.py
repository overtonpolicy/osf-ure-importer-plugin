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
from .project import Project

class User(OSFBase):
    """A python class to represent an OSF Author / USer
    """

    json_properties = ['id', 'links', 'type', 'attributes', 'relationships']

    def __init__(self, init, session):
        self._projects = None

        self.session = session
        if type(init) is dict:
            self.process_json(init)
            self._user_id = self.id
        else:
            self._user_id = init

    @property
    def user_id(self) -> str:
        "str: The User ID"
        return(self._user_id)

    @property
    def projects(self) -> list[Project]:
        """list: The Projects attached to the user """
        return([p for p in self.nodes if p.project_type == 'project'])

    @property
    def nodes(self):
        """list: All Nodes attached to the user """

        if not self._projects:
            data = self.session.get_all(self.session.root + '/users/'+self.user_id+'/nodes/')
            self._projects = [Project(p, self.session) for p in data]
        return(self._projects)

    def get_project(self, project_id:str) -> Project:
        """ Gets one of the user's projects, by ID.

        Args:
            project_id (str): The project ID

        Returns:
            Project: The Project
            None: IF the project_id is not one of the user's projects, nothing is returned.
        """
        for p in self.projects:
            if p.id == project_id:
                return(p)
