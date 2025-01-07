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

import flask
import requests
import re
import sys

from requests.models import stream_decode_response_unicode 

bp = flask.Blueprint('osf', __name__, url_prefix='/osf')


abspath = re.compile(r'https?://', re.I)
osf_server = "https://api.osf.io/v2"


def parse_parameters(param_items=None, checkbox_params=None):
    """ Render the url/form/data parameters to create a python dict of it.
    
    This ends up being different from calling `flask.request.values.to_dict()` because:
    - It translate the empty string to None
    - It handles wonky serialization of certain form elements. When `jQuery.serialize()` encounters checkboxes, it passes checked checkboxes as emptry strings, and False checkboxes are not included at all. So, we translate that to an accurate boolean.

    Args:
        param_items (dict): A dictionary of parameter items to parse. The default, which is appropriate for flask-webpages contexts, is flask.request.values
        checkbox_params (list): A list of form items to translate. If they exist in the incoming parameter, their value will be set to true. If they do not exist, they will be added and set to False.  
    """
    if param_items is None:
        param_items = flask.request.values

    parameters = {k:None if v == '' else v for k,v in param_items.items()}
    #
    # jQuery.serialize is dumb. Checked checkboxes are encoded as empty hash values, and unchecked checkboxes are not present in the paraemeter list.
    # So we fix that here
    if checkbox_params:
        for checkboxparam in checkbox_params:
            parameters[checkboxparam] = checkboxparam in parameters
    return(parameters)

def osfapicall(url:str, reqparams:dict=None, method:str='get', quiet:bool=True, return_json:bool=True, access_token:str=None, debug:bool=False):
    """ Shorthand call to the OSF API. Use this to curry a request on to OSF from a plugin or web app.
    
    Args:
        url: The url search path for the *OSF API* - for example, "/nodes/38p21". This should not be a full URL.
        reqparams: The parameters to send along with the request. How this is passed into the requests library call depends on the type of call - these are the URL arguments for a GET call or the data arguments for a POST call. At present, this function does not support passing both GET and DATA parameters separately into a POST.
        method: The type of http method call. Default is GET.
        access_token: If provided, the OSF access_token for a current session. If not provided, It will attempt to get it from the flask session.
        debug: If True, print out extra information about the request.
        
    """

    if not url:
        raise Exception('must provide a url')    
    
    if not reqparams:
        reqparams = None
    
    if not abspath.match(url):
        url = osf_server + url

    if not access_token:
        access_token = flask.session.get('access_token')
    
    if not access_token:
        return({
            'errors': [{'detail': "You must be logged in to OSF to perform this action."}],
            'action': 'login',
            'status_code': -1,
        })
    
    if debug:
        print(f"about to make {method} req:\n\t{url}\n\t{reqparams}\n\tToken: {access_token}", file=sys.stderr)
    if method == 'get':
        # 'params' is the payload, not 'data'
        # Returns contentful json  
        req = requests.get(
            url,
            headers={"Authorization" : "Bearer " + access_token},
            params=reqparams,
        )
    elif method == 'delete':
        # 'data' is the payload. 'params' is available for explicit url params, but this doesn't exist in the OSF API
        req = getattr(requests, method)(
            url,
            headers={"Authorization" : "Bearer " + access_token},
            data=reqparams,
        )    
    elif method == 'post':
        # 'data' is the payload. 'params' is available for explicit url params, but this doesn't exist in the OSF API
        import json
        if reqparams:
            reqparam = json.dumps(reqparams)
        req = getattr(requests, method)(
            url,
            headers={"Authorization" : "Bearer " + access_token},
            data=reqparams,
        )    
    else:
        raise Exception(f"Unknown method {method}")


    if req.status_code == 401 or req.status_code == 403:
        #
        # 401 - this happens when our access token is incorrect or expired
        #
        if debug:
            print("\t*** Request Respone: User is no longer logged in", file=sys.stderr)

        js = req.json()
        js['errors'].append({'detail': f'status_code: {req.status_code}'})
        js['action'] = 'reauthorize'
        js['status_code'] = req.status_code
        return(js)

    if not req.ok:
        if quiet:
            return({
                'errors': [
                    f"{req.reason} (Code {req.status_code})",
                ],
                'status_code': req.status_code,
                'url': url,
                'params': reqparams,
            })
        error_response = f"Attempt to {method} {url} returned unexpected status code {req.status_code}.\n<h3>Debug Info</h3>\nResponse Status Code: {req.status_code}\nResponse Reason: {req.reason}\nResponse Headers: {req.headers}\nResponse Text: {req.text}"
        if debug:
            print("\t*** Response Failed: " + error_response, file=sys.stderr)
        raise Exception(error_response)

    if method in ('delete',):
        # These requests do not have a response payload, just indicate a status of successful.
        return({
            'url': url,
            'params': reqparams,
            'status_code': req.status_code,
            'reason': method + " api call successful.",
            'errors': False,
        })

    if return_json:
        js = req.json()
        return(js)
    else:
        return(req.text)     

def osfpost(url, url_params=None, **kwargs):
    return(osfapicall(url, url_params, method='post', **kwargs))

def osfget(url, url_params=None, **kwargs):
    return(osfapicall(url, url_params, method='get', **kwargs))

def osfdelete(url, url_params=None, **kwargs):
    return(osfapicall(url, url_params, method='delete', **kwargs))


def osfgetdata(url, url_params=None, fetch_all=False):
    
    resp = osfget(url, url_params)
    if 'data' not in resp:
        if not resp['errors']:
            resp['errors'] = f"Call to osfgetdata for {url}, but this returned neither data nor an error message"
        return(resp)
    
    data = resp['data']
    if type(data) not in (tuple, list):
        return(data)

    if fetch_all:
        if 'links' in resp and 'next' in resp['links'] and resp['links']['next']:
            nextdata = osfgetdata(resp['links']['next'], fetch_all=True)
            if type(nextdata) is list:
                return(data + nextdata)
            if nextdata['errors']:
                return({
                    'errors': nextdata['errors'],
                    'status_code': nextdata['status_code'],
                    'debug': nextdata,
                })
                #raise Exception(f"Unexpected result. Data returned was an array for the first page but not an array for the follow pages")
            return(nextdata)
    
    return(data)


@bp.route('/admin', methods=['GET', 'POST'])
def ap_admin():
    if flask.request.url_root != 'http://localhost:3000/':
        raise Exception("Path not allowed")
    params = flask.request.values.to_dict()
    url = params['url']
    del params['url']  
    if 'method' in params:
        method = params['method']
        del params['method']
    else:
        method = 'get'      
    return(osfapicall(url, params, method=method))

@bp.route('/api', methods=['GET', 'POST'])
def osfget_url():
    params = flask.request.values.to_dict()
    url = params['url']
    del params['url']    
    return(osfget(url, params))

@bp.route('/data', methods=['GET', 'POST'])
def osfget_data():
    params = flask.request.values.to_dict()
    url = params['url']
    del params['url']    
    if 'fetch_all' in params:
        fetch_all = params['fetch_all']
        del params['fetch_all']
    else:
        fetch_all = False
    return(osfgetdata(url, params, fetch_all=fetch_all))


@bp.route('/me', methods=['GET', 'POST'])
def getme(refresh=False):
    data = flask.session.get('me')
    if refresh or not data:        
        js = osfget('/users/me/')
        if not 'data' in js:
            # error
            return(js)
        js = js['data']            
        data = {
            'name': js['attributes']['full_name'],
            'id': js['id'],
            'nodes': js['relationships']['nodes']['links']['related']['href'],
            'errors': None,
        }
        flask.session['me'] = data
    return(data)

@bp.route('/nodes', methods=['GET', 'POST'])
def getnodes():
    data = flask.session.get('nodes')
    if data:
        return(data)

    me = getme()
    if not data:
        bibliographic_only = flask.request.form.get('bibliographic')
        include_components = flask.request.form.get('include_components')
        if include_components == 'false':
            include_components = False
        
        params = {}
        if bibliographic_only:
            params = {                
                'embed': 'contributors',
                'fields': {
                    'nodes': ['category','current_user_is_contributor','current_user_permissions','date_created','date_modified','public','title','wiki_enabled','description','id','links','contributors'],                
                    'contributors': ['bibliographic','id','permission','users'],
                    'users': ['id', 'full_name'],
                },
                #'fields[users]': 'id,full_name',

                #'filter[parent]':'null', 
                #'embed': 'contributors',
                #'fields[nodes]': 'category,current_user_is_contributor,current_user_permissions,date_created,date_modified,public,title,wiki_enabled,description,id,links,contributors',
                #'fields[contributors]': 'bibliographic,id,permission,users',
                #'fields[users]': 'id,full_name',
            }
        else:
            params = {
                #'filter[parent]': 'null',
                #'filter[contributors]': me['id'],
                #'filter': {
                #    'parent':None,
                #    'contributors': me['id'],
                #},
            }
        if not include_components:
            params['filter[parent]'] = 'null'

        data = osfgetdata(f"/users/{me['id']}/nodes/", params, fetch_all=True)
        if type(data) is not list:
            return(data)

        
        if bibliographic_only:
            bibliographic = [] 
            from pprint import pprint 

            for node in data:
                # find the contributor record 
                for contrib in node['embeds']['contributors']['data']:
                    # if this is the user AND it's a bibliographic contribution, add it and break
                    data = contrib['embeds']['users'].get('data')
                    if not data: # happens when a user record links to someone that has deleted their account
                        continue
                    if data['id'] != me['id']:                        
                        continue
                    if contrib['attributes']['bibliographic']:                        
                        bibliographic.append(node)
                        break   
            return({'data': bibliographic, 'errors':None,})
        else:
            return({'data': data, 'errors':None,})

