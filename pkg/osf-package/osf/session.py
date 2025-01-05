import requests
import json

import osf

import re

relurlre = re.compile(r'/')

python_request_params = [
    'params', 'data', 'json', 'headers', 'cookies', 'files', 'auth', 
    'timeout', 'allow_redirects', 'proxies', 'verify', 'stream', 'cert'
]

class AccessTokenSession(requests.Session):
    """
    Encapsulates and OSF request session.  
    """

    def __init__(self, access_token:str=None, *args, **kwargs):
        self.access_token = access_token
        super().__init__(*args, **kwargs)

    @property
    def root(self) -> str:
        """str: The API Root URL """
        return('https://api.osf.io/v2')

    @property
    def auth_header(self) -> dict:
        """dict: The authorization headers to send to the API """
        if self.access_token:
            return({'Authorization': 'Bearer ' + self.access_token})
        return({})

    def process_url(self, url:str) -> str:
        """ Generates a full URL for a given url path.

        Args:
            url (str): The path of the endpoint
        Returns:
            str: The full URL.
        """
        if relurlre.match(url):
            return(self.root + url)
        return(url)

    def process_request_args(self, **kwargs) -> tuple[dict, dict]:
        """ Formats the parameters to submit to the OSF API by 
        separating arguments to the request function from 
        parameters to be sent to the API endpoint.

        Returns:
            tuple[dict, dict]: 
                First result are the parameters for the request function
                Second result are for submission to th API (Get Params, Data Payload, etc) 
        """
        request_params = {}
        extra_params = {}
        for arg, val in kwargs.items():
            if arg in python_request_params:
                request_params[arg] = val
            else:
                extra_params[arg] = val
        
        #
        # now add the header
        #
        if 'headers' in request_params and request_params['headers']:
            request_params['headers'].update(self.auth_header)
        else:
            request_params['headers'] = self.auth_header
        return(request_params, extra_params)

    def get(self, url:str, **kwargs) -> requests.Response:
        """ Submit a GET request to the OSF API 
        Returns:
            requests.Response: The Response
        """
        request_params, params = self.process_request_args(**kwargs)        
        if 'params' in request_params:
            if params:
                raise Exception("params explicitly passed into get request, but other parameters exist outside. Cannot mix and match in this way.")            
            return(super().get(self.process_url(url), **request_params))
        else:
            return(super().get(self.process_url(url), **request_params, params=params))

    def put(self, url, **kwargs) -> requests.Response:
        """ Submit a PUT request to the OSF API 
        Returns:
            requests.Response: The Response
        """
        request_params, params = self.process_request_args(**kwargs)        
        if 'params' in request_params:
            if params:
                raise Exception("params explicitly passed into get request, but other parameters exist outside. Cannot mix and match in this way.")
            return(super().put(self.process_url(url), **request_params))
        else:
            return(super().put(self.process_url(url), **request_params, params=params))

    def post(self, url, **kwargs) -> requests.Response:
        """ Submit a POST request to the OSF API 
        Returns:
            requests.Response: The Response
        """
        request_params, data = self.process_request_args(**kwargs)
        if 'data' in request_params:
            if data:
                raise Exception("data explicitly passed into post request, but other parameters exist outside. Cannot mix and match in this way.")
            return(super().post(self.process_url(url), **request_params))
        else:
            return(super().post(self.process_url(url), **request_params, data=data))

    def patch(self, url, **kwargs) -> requests.Response:
        """ Submit a PATH request to the OSF API 
        Returns:
            requests.Response: The Response
        """
        request_params, params = self.process_request_args(**kwargs)
        return(super().patch(self.process_url(url), **request_params, params=params))

    def delete(self, url, **kwargs) -> requests.Response:
        """ Submit a DELETE request to the OSF API 
        Returns:
            requests.Response: The Response
        """
        request_params, params = self.process_request_args(**kwargs)
        return(super().delete(self.process_url(url), **request_params, **params))


    def get_all(self, url, **kwargs) -> list[dict]:
        """ Submits a GET request to the OSF API, and follows 
        any page continuation tokens to return the full dataset.

        Returns:
            list[dict]: The list of response elements, json de-serialized
        """
        req = self.get(self.process_url(url), **kwargs)
        j = req.json()
        if 'errors' in j:
            if 'error' not in j:
                j['error'] = True
            return(j)

        result = j['data']
        
        while j['links']['next']:
            req = self.get(j['links']['next'])
            j = req.json()
            result.extend(j['data'])
        ids = [r['id'] for r in result]
        return(result)

    def get_user(self) -> dict:
        """ Gets the json data for the currently loged in user.

        Returns:
            dict: The user data
        """
        req = self.get(self.root + '/users/me/')
        if req.status_code == 200:
            return(osf.User(req.json()['data'], session=self))
        elif req.status_code == 401:
            js = req.json()
            if 'errors' in js and js['errors'][0]['detail'] == "User provided an invalid OAuth2 access token":
                print("Auth token has been revoked.")
                return

        else:
            raise Exception(f"Unknown status code {req.status_code} returned from get user!")
