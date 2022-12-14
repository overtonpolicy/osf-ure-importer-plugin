
class OSFBase():

    def process_json(self, data):
        
        for prop in self.json_properties:
            if prop in data:
                setattr(self, prop, data[prop])
            else:
                setattr(self, prop, None)


from .session import AccessTokenSession as session
from .user import User
from .wiki import Wiki
from .project import Project