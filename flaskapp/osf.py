import flask
import requests
import re
import sys

from requests.models import stream_decode_response_unicode 

bp = flask.Blueprint('osf', __name__, url_prefix='/osf')


abspath = re.compile(r'https?://', re.I)
osf_server = "https://api.osf.io/v2"

def osfget(url, url_params=None):

    if not url:
        raise Exception('must provide a url')    
    
    if not url_params:
        url_params = None
    
    if not abspath.match(url):
        url = osf_server + url

    access_token = flask.session.get('access_token')
    if not access_token:
        raise Exception("You must be logged in to make this request.")
    
    print(f"about to osfget:\n\t{url}\n\t{url_params}\n\tToken: {access_token}", file=sys.stderr)
    req = requests.get(
        url,
        headers={"Authorization" : "Bearer " + access_token},
        params=url_params,
    )

    if req.status_code == 401:
        #
        # 401 - this happens when our access token is incorrect or expired
        #
        js = req.json()
        return(js)

    if req.status_code >= 400:
        raise Exception(f"Attempt to get {url} returned unexpected status code {req.status_code}")
    
    js = req.json()
    if 'errors' in js:
        if js['errors'][0]['detail'] and js['errors'][0]['detail'] == 'User provided an invalid OAuth2 access token':
            raise Exception("TODO: Need to work in the logic to handle expired OSF authorization tokens in real time. Tell Kevin if this gets annoying")
            #self.launchAuthWindow(reget, on_failure);
            # try to fetch again
        else:
            raise Exception(f"Attempt to get {url} returned with errors: {js['errors']}")
    return(js)     

def osfgetdata(url, url_params=None, fetch_all=False):
    
    resp = osfget(url, url_params)
    if 'data' not in resp:
        if 'errors' not in resp:
            resp['errors'] = f"Call to osfgetdata for {url}, but this returned neither data nor an error message"
        return(resp)
    
    data = resp['data']
    if type(data) not in (tuple, list):
        return(data)

    if fetch_all:
        if 'links' in resp and 'next' in resp['links'] and resp['links']['next']:
            nextdata = osfgetdata(resp['links']['next'])
            if type(nextdata) is list:
                return(data + nextdata)
            if not 'errors' in nextdata and nextdata['errors']:
                raise Exception('Unexpected result')
            return(nextdata)
    
    return(data)
            

@bp.route('/api', methods=['GET', 'POST'])
def osfget_url():
    url = flask.request.values.get('url')
    params = flask.request.values.get('params')
    return(osfget(url, params))

@bp.route('/me', methods=['GET', 'POST'])
def getme():
    print("ME:", flask.session.get('me'), sys.stderr)
    if flask.session.get('me'):
        flask.session.clear()
    data = flask.session.get('me')
    if not data:        
        js = osfget('/users/me/')
        if not 'data' in js:
            # error
            return(js)
        js = js['data']            
        data = {
            'name': js['attributes']['full_name'],
            'id': js['id'],
            'nodes': js['relationships']['nodes']['links']['related']['href'],
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
        
        params = {}
        if bibliographic_only:
            params = {
                'filter': {'parent': None},
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

        data = osfgetdata(f"/users/{me['id']}/nodes/", params, fetch_all=True)
        if type(data) is not list:
            return(data)

        print(data, file=sys.stderr)
        if bibliographic_only:
            bibliographic = [] 
            for node in data:
                # find the contributor record 
                for contrib in node['embeds']['contributors']['data']:
                    # if this is the user AND it's a bibliographic contribution, add it and break
                    if contrib['embeds']['users']['data']['id'] != me['id']:
                            continue
                    if contrib['attributes']['bibliographic']:
                        bibliographic.append(node)
                        break
            return(bibliographic)
        else:
            return(data)




'''
from js 


    /*******************
     * 
     * Routines to access data about the validated user.
     * 
     *******************/

    get me(){
        return(self._me);
    }

    set me(value){
        if(value != self._me){
            self._me = value;
            self._nodes = null;
        }
    }

    get nodes(){
        return(self._nodes);
    }

    osfget(url, params, on_success, on_failure, reauthorize=true){
        var self = this;
        if(url[0] == '/')
            url = self.osf_server + url;
        var checkExpiration = function(resp){
            if (resp.errors){

                if(resp.errors[0].detail && resp.errors[0].detail == 'User provided an invalid OAuth2 access token'){
                    // 
                    if(!reauthorize){
                        osfAjaxError(resp);
                        if(on_failure)
                            on_failure(resp);
                        return;
                    }
                    // need to reauthorize
                    var reget = function (){
                        self.osfget(url, params, on_success, on_failure, false);
                    };
                    self.launchAuthWindow(reget, on_failure);
                }
                else{
                    osfAjaxError(resp);
                    if(on_failure)
                        on_failure(resp);
                    return;
                }
            }
            else{
                if(resp.links.next){
                    console.log("Curring to next link: " + resp.links.next);
                    var wrapped = function(newdata){
                        var alldata = resp.data.concat(newdata);
                        on_success(alldata);
                    };
                    self.osfget(resp.links.next, null, wrapped, on_failure, reauthorize);
                }
                else{
                    on_success(resp.data);
                }
            }
        };
        console.log(
            self.authorizationHeader()
        );
        $.ajax({
            type:'GET',
            url:url,
            headers: self.authorizationHeader(),
            data: params,
            dataType: 'json',
            error: osfAjaxError,
            success: checkExpiration,
        });        
    }

    /**
     * Generates the headers to authenticate given the current state/values
     */
    authorizationHeader(){
        if(this.access_token)
            return({'Authorization': 'Bearer ' + this.access_token});
        return({});
    }

    getMe(extra_onsuccess){
        var self = this;
        if(self.me)
            return(extra_onsuccess(self.me));

        var on_success = function(resp,s,x){
            console.log("Get me returned cleanly with the following response:");
            console.log(resp);
            if(!resp.data){
                osfAjaxError(resp);
                //extra_onsuccess();
                return;
            }
            self.me = resp.data;
            extra_onsuccess(self.me);
        }
        /*
        self.osfget(
            '/cgi-bin/realtime.py', {'url': '/users/me'}, on_success
        );
        */
       var on_failure = function(resp, s, x){
           console.log("Get me had a failure");
           if(resp.responseJSON.errors[0].detail == "User provided an invalid OAuth2 access token"){
               console.log("You have been logged out");
               var reload_me = function(){
                    self.getMe(extra_onsuccess); 
               };
               self.launchAuthWindow(reload_me, osfAjaxError)
           }
           else{
                osfAjaxError(resp);
           }
       }

        ///// WAIT. CAN WE ACTUALLY DO THINGS LIKE THIS?
       $.ajax({
            url: self.osf_server + "/users/me/",
            method: "GET",
            headers: {
                "Authorization" : "Bearer " + self.access_token
            },
            success: on_success,
            error: on_failure,
        });

        return;
    }
    getNodes(onsuccess, params){        
        var self = this;

        if(!self.me){
            self.getMe(function(resp,s,x){self.getNodes(onsuccess,params)});
            return;
        }
        // if custom params are passed in, don't save anything.
        if(params){
            // by default, get top level nodes we are contributors on
            self.osfget('/users/' +self.me.id+ '/nodes/', params, onsuccess);
        }
        else{
            if(self._nodes)
                return(onsuccess(self._nodes));

            // by default, get top level nodes we are contributors on
            self.osfget('/users/' +self.me.id+ '/nodes/', {
                'filter[parent]':'null',
                'filter[contributors]': self.me.id,
            },
            function(resp,s,x){
                if(params)
                    console.log("getNodes [with params ] returned, len " + resp.length);
                else
                    console.log("getNodes returned, len " + resp.length);
                console.log(resp);
                self._nodes = resp;
                onsuccess(self._nodes);
            });
        }
    };
    getBibliographicNodes(onsuccess){
        var self = this;
        if(self._bibliographic){
            onsuccess(self._bibliographic);
            return;
        }
        var wrapped = function(resp){
            var bibliographic = [];
            resp.forEach(function(node){
                // find the contributor record for self
                node.embeds.contributors.data.forEach(function(contrib){
                    if(contrib.embeds.users.data.id != self.me.id)
                        return;
                    if(contrib.attributes.bibliographic)
                    bibliographic.push(node);
                });
            });
            self._bibliographic = bibliographic;
            onsuccess(self._bibliographic);
        };
        self.getNodes(wrapped, {
            'filter[parent]':'null', 
            'embed': 'contributors',
            'fields[nodes]': 'category,current_user_is_contributor,current_user_permissions,date_created,date_modified,public,title,wiki_enabled,description,id,links,contributors',
            'fields[contributors]': 'bibliographic,id,permission,users',
            'fields[users]': 'id,full_name'
        });
    };

'''