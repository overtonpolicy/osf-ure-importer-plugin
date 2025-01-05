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
