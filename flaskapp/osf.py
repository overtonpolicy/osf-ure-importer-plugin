import functools
import flask
from . import db

bp = flask.Blueprint('osf', __name__, url_prefix='/osf')




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