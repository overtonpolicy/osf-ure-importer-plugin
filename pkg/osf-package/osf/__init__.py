class OSFBase():
    """Baseclass for OSF Objects.

    Subclasses are expected to have a `json_properties` set that lists properties
    that may exist in the JSON response from an OSF API REST call, and these
    are translated to object values. If the property does not exist, it is set
    to None so that python functions can call {object}.{property} without 
    throwing an AttributeError
    """

    def process_json(self, data:dict):
        """ Take the json response from an OSF API REST call and set the 
        object properties based on it.
        """
        
        for prop in self.json_properties:
            if prop in data:
                setattr(self, prop, data[prop])
            else:
                setattr(self, prop, None)


from .session import AccessTokenSession as session
from .wiki import Wiki
from .project import Project
from .user import User
