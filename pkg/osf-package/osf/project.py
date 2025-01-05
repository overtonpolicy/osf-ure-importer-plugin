import typing

from . import OSFBase
from .wiki import Wiki
from .session import AccessTokenSession

class Project(OSFBase):
    """A python class to represent an OSF Project
    """

    json_properties = ['attributes', 'id', 'links', 'relationships', 'type']
    debug = False

    @classmethod
    def get(cls, id:str, session:AccessTokenSession) -> typing.Self:
        """Get a new Project from OSF.
        
        Args:
            id: The Project ID
            session: The requests session
        Returns:
            Project: The new Project object
            None: If the session access token has expired 
        Raises:
            RuntimeError for any non-ok status aside from token expiration
        """
        req = session.get(session.root + f'/nodes/{id}/')
        if req.status_code == 200:
            return(Project(req.json()['data'], session=session))
        elif req.status_code == 401 and req.reason == 'Unauthorized':
            return
        else:
            raise RuntimeError("Error retrieving a node", req.json())


    def __init__(self, jref:dict, session:AccessTokenSession):
        self.session = session
        self.process_json(jref)
        self._children = None
        self._wikis = None

    @property
    def title(self) -> str:
        """str: The project title"""
        return(self.json['attributes']['title'])

    @property
    def project_type(self) -> str:
        """str: The project category"""
        return(self.json['attributes']['category'])

    def _follow_relationship(self, name, *paths):
        ref = self.json['relationships'][name]
        for p in paths:
            ref = ref[p]
        data = self.session.get_all(ref['href'])
        return(data)

    @property
    def children(self) -> list[typing.Self]:
        """list: Any subproject components, as Project objects."""
        if not self._children:
            raw = self._follow_relationship('children', 'links', 'related')
            self._children = [Project(comp, session=self.session) for comp in raw]
        return(self._children)

    @property
    def wikis(self) -> list[Wiki]:
        """list: The Wiki objects for this project."""
        if not self._wikis:
            raw = self._follow_relationship('wikis', 'links', 'related')
            self._wikis = [Wiki(wiki, session=self.session) for wiki in raw]
        return(self._wikis)

    def get_wiki_by_name(self, name:str) -> Wiki:
        """Get a Wiki in this Project 

        Args:
            name (str): The wiki name/title
        Returns:
            Wiki: The wiki
        """
        for wiki in self.wikis:
            if wiki.name == name:
                return(wiki)
            elif name in ('Home', 'home') and wiki.name in ('home', 'Home', None):
                # for some weird reason the Home wiki shows up with an attribute of home
                return(wiki)

    def get_component_by_name(self, name:str) -> typing.Self:
        """Get a component subproject for this Project 

        Args:
            name (str): The subproject name
        Returns:
            Wiki: The wiki
        """
        for comp in self.children:
            if comp.title == name:
                return(comp)

    def clear(self):
        """ Delete all wiki pages in this node and delete all components beneath it. """
        p1, p2 = self.session.process_request_args()
        result = {
            'wikis': [],
            'components': [],    
            'errors': [ ],
        }
        for wiki in self.wikis:
            if wiki.name in ('home', 'Home'):
                # TODO: We do not clear the home wiki
                pass
            else:
                self.session.delete(f'/wikis/{wiki.id}/')
                result['wikis'].append(f"{wiki.name} [{wiki.id}]")
                
        for component in self.children:
            res = self.session.delete(f'/nodes/{component.id}/')
            if res.status_code == 204:
                result['components'].append(f"{component.title} [{component.id}]")
            else:
                result['errors'].append(f"{component.title} [{component.id}] was not deleted because of an error: {res.json()}")
        return(result)

    def create_component(self, name:str, category:str, **kwargs) -> typing.Self:
        """ Create a new component subproject in OSF.

        Args:
            name (str): The name of the subproject.
            category (str): The category/type of the subproject.
        Returns:
            Project: The new component subproject.
        """
        req = self.session.post(self.session.root + '/nodes/' + self.id + '/children/', data={
            'type': 'nodes',
            'category': category,
            'title': name,   
            **kwargs,                    
        })
        
        if req.status_code != 201:
            raise Exception(f"Failed to create a new component with name {name}")
        
        new_component = Project(req.json()['data'], session=self.session)
        self.children.append(new_component)
        return(new_component) 

    def create_wiki(self, name:str, content:str, overwrite:bool=False) -> Wiki:
        """Create a new Wiki in this Project.

        Args:
            name (str): The Wiki title.
            content (str): The wiki markdown content.
            overwrite (bool, optional): If True, overwrite an existing wiki of the same name if it exists. If False, raise an Exception if the name/title exists. Defaults to False.

        Raises:
            FileExistsError: If the wiki exists (and overwrite is False) 
        Returns:
            Wiki: The new Wiki
        """

        wiki = self.get_wiki_by_name(name)
        if wiki:
            if not overwrite:
                raise FileExistsError(f"Attempted to create a wiki with name '{name}, but that wiki already exists in project {self.id}")            
            elif self.debug:
                print(f"\t..Overwriting existing sheet")

            req = self.session.post(self.session.root + '/wikis/'+ wiki.id + '/versions/', data={
                'type': 'wiki-versions',
                'content': content,            
            })
            if req.status_code == 201:
                wiki._json.update(req.json()['data'])
                return(wiki)
            else:
                raise Exception(f"Request to update existing wiki '{name}' appears to have failed with status code {req.status_code}: {req.reason}")
        else:
            if self.debug:
                print(f"\t..Creating new wiki")

            req = self.session.post(self.session.root + '/nodes/' + self.id + '/wikis/', data={
                'name': name,
                'type': 'wikis',
                'content': content,            
            })

            if req.status_code == 201:
                new_wiki = Wiki(req.json()['data'], session=self.session)
                self._wikis.append(new_wiki)
                return(new_wiki)
            elif req.status_code == 409:
                raise FileExistsError(f"Request to create '{name}' failed with status code 409. You already have a wiki with the name {name} in project {self.id}: https://osf.io/{self.id}/wiki")
            elif req.status_code == 404:
                raise Exception(f"Request to create '{name}' failed with status code 404. This usually happens if you specified the incorrect project id {self.id} (or possibly if you cannot see the project).  The url for the project you specified would be: https://osf.io/{self.id}/wiki")
            else:
                raise Exception(f"Request to create wiki '{name}' in project '{self.id}' appears to have failed with status code {req.status_code}: {req.reason}")
    
