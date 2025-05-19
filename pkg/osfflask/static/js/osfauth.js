/**

Copyright (c) 2024, Kevin Crouse. 

This file is part of the *URE Methods Plugin Repository*, located at 
https://github.com/kcphila/osf-ure-plugins

This file is distributed under the terms of the GNU General Public License 3.0
and can be used, shared, or modified provided you attribute the original work 
to the original author, Kevin Crouse.

See the README.md in the root of the project directory, or go to 
http://www.gnu.org/licenses/gpl-3.0.html for license details.


OSFAuth handles interactions with the OSF Api in javascript, using OAUTH2 by default. 
 * Note that this is designed to work with python-based packages in this repository to ensure 
 * that your client secret remains secret and to avoid javascript cross-domain errors.
 * 
 * Usages:
 *   1. Subclass OSFAuth with overrides for the default authorization values.
 *   2. Instantiate an OSFAuth object with per-object overrides, as necessary.
 *   3. If you wat to use the Personal Access Token (PAT) instead of Oauth, see the OSFAuthPAT subclass below.
*/
class OSFAuth {
    scope="osf.full_write";
    state="OQlHiyBY";
    oauth_callback_url=null;
    authorization_server = "https://accounts.osf.io"
    osf_server = "https://api.osf.io/v2"

    constructor(params){
        this.loginCallbacks = []
        this.logoutCallbacks = []
        this.logged_in = false 
    }
    
    /**
     * Returns the access code, and looks in the url parameter for it if it doesn't exist.
     */
    get access_code() {
        if(!this._access_code){
            //substring(1) to remove the '#'
            var hash = this.constructor.parseParams(document.location.search.substring(1));
            if(hash)
                this._access_code = hash.code;
        }
        return(this._access_code);
    }

    set access_code(value){
        this._access_code = value;
    }

    /** Completes the authorization by posting to the server to exchange the access code for an authorization token. */
    completeAuthorization(params){
        var self = this;
        if(!params.error)
            params.error = ureAjaxError;            
        if(!self.access_code){
            ureAjaxError("Cannot complete authorization without an access code");
            return;
        }
        $.ajax({
            url: "/auth/registertoken",
            method: "POST",
            dataType: "json",
            data: {
                'method': 'get_access_token',
                "access_code" : self.access_code,
                "client_id": self.oauth_client_id,
                "redirect_uri": self.oauth_callback_url,
            },
            success: function(data) {                
                if(data.error){
                    ureAjaxError(data);                     
                    if(on_error)
                        on_error(data);   
                }
                else if (data.errors){                    
                    ureAjaxError(data); 
                }
                else{
                    self.access_token = data.access_token;
                    self.registerLogin();
                    if(params.success)
                        params.success(data);
                }
            },
            error: params.error
        });    
    }

    revokeCurrentToken(on_complete){
        var self = this;
        $.ajax({        
            url: "/auth/revoketoken",
            method: "POST",
            dataType: "json",
            success: function(data) {
                console.log("Token revoked");
                self.registerLogout();
                window.location.assign("/");
                if(on_complete)
                    on_complete(data);
            },
            error: ureAjaxError            
        });
    };

    /**
     * Parse the parameter as a string and returns the parameters as a hash - used primarily to parse the document href.
     * 
     * @param {string} str - the string to parse, expected to be in URL formatted language.
     *  
     * @returns {object} - a map between each parameter and value
     */ 
    static parseParams(str) {
        if (str[0] == '?' || str[0] == '&')
           str = str.substr(1,);
        var pieces = str.split("&");
        var data = {};
        // process each query pair
        for (var i = 0; i < pieces.length; i++) {
            var parts = pieces[i].split("=");
            if (parts.length < 2) {
                parts.push("");
            }
            data[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
        }
        return(data);
    }

    /**
     * Get the value for the param_name from the URL path .
     * 
     * @param {string} param_name - the param to find.
     *  
     * @returns {string} - the value for the param
     */ 
    static getURLParam(param_name) {
        var params = this.parseParams(window.location.search);
        return(params[param_name]);
    }


    /** launchAuthWindow - Begin OAUTH2 Authorization
     * 
     * @param {function} success - a function to be called if authorization is successful. If all is successful, this function will be called with the authorization token. If the call is valid but the server providdes an error, this function will be called with no parameters.
     * @param {function} error - a function to be called if the ajax call fails.
     * 
     * TODO: Should success_callback really be called in cases of error? 
     */
    launchAuthWindow(params){
        var self = this;
	    if(!params)
	        params = {error: ureAjaxError};	  
	    else if(!params.error)
            params.error = ureAjaxError;

        $.ajax({
            url: "/auth/getclient",
            method: "POST",
            dataType: "json",
            success: function(data){
                
                var osf_auth_url = self.authorization_server + "/oauth2/authorize?response_type=code&scope=" + self.scope + "&state="+self.state+"&client_id=" + data.oauth_client_id + "&redirect_uri=" + data.oauth_callback_url

                //create popup window for authorization
                var child = window.open(
                    osf_auth_url,
                    'OauthWindow',
                    'width=550,height=700'
                );

                //listener to receive messages from child
                window.addEventListener(
                    'message',
                    function(event) {
                        console.log("Received:");
                        console.log(event);
                        if(event.origin !== window.location.origin) 
                            return;
                        if(event.data.code){
                            self.access_code = event.data.code;
                            self.completeAuthorization({success:params.success, error:params.error});
                            // let the child know it can close
                            child.postMessage('close', window.location.origin); 
                        }
                        else if (event.data.revoked){
                            // let the child know it can close
                            child.postMessage('close', window.location.origin); 
                            // now set the code
                            self.access_token = undefined;
                            if(error_callback)
                            error_callback();
                        }
                    },
                    false,
                );

            },
            error: params.error,    
        });
    }
    
    /** the function called by the authorization window to send the access code back to the parent*/
    static initializeCallback(){

        // identify the referrer        
        var access_code = this.getURLParam('code');        
        
        // console.log("Received access code:" + access_code);
        if(!access_code){
            alert("Authentication Callback URL not provided with an access code!");
            return;
        }    
        window.opener.postMessage({'code': access_code}, window.location.origin);
        window.close();
    }

    /** Call the osf api. Parameters are the same as local() except the url is not required.
     * 
     * @param {*} params 
     * @returns 
     */
    apiget({apipath = null, params = null, success = null, error = ureAjaxError, relogin = true, json = true}){

        var localparams = {
            url: json ? '/osf/data' : '/osf/api',
            params: {url: apipath, params: params},
            success: success, 
            error: error, 
            relogin: relogin, 
        };
        return(this.local(localparams));
    }

    /**
     * 
     * @param {} url 
     * @param {} params 
     * @param {} failure 
     * @param {} success
     * @param {} json: If true, return json  
     * @param {} relogin: If true, automatically relogin if the token is stale  
     */
    local({url = null, params = null, success = null, error = ureAjaxError, relogin = true, json = true}){
        var self = this;
        console.log("local called");
        console.log(relogin);

        $.ajax({
            url: url,
            method: 'POST',
            data: params,
            error: error,            
            success: function(resp, status, jqXHR){
                // check for errors
                if(!resp.errors){
                    return(success(resp, status, jqXHR));
                }
                // is it just authentication timeout / failure?
                // If not, fail now.
                if(![-1, 401,403].includes(resp.status_code)){
                    return(ureAjaxError(resp))
                }
                // attempt to log back in one time, unless relogin is fall
                if(!relogin){
                    self.registerLogout();
                    return;
                }
                console.log("User no longer logged in - attempting to log in again.")
		        $('#osf-authentication-status').html('<b>New log in to OSF required</b>. If the login window does not appear, you need to allow pop-ups for uremethods and reload (instructions <a href="https://support.google.com/chrome/answer/95472?hl=en&co=GENIE.Platform%3DDesktop&oco=0" target="_blank">here</a>)')
                self.launchAuthWindow({
                    success: function(){
			            $('#osf-authentication-status').html('');
                        $.ajax({ 
                            url: url,
                            method: 'POST',
                            data: params,                            
                            error: error,
                            success: function(resp){
                                if(resp.errors)
                                    return ureAjaxError(resp);
                                else{
                                    success(resp);
                                }
                            },
                        })
                    }, 
                    error: function(){
			$('#osf-authentication-status').html('');
                        console.log("Failed to log user back in. Redirect to home.")
                        window.location = "/"
                    }
                });
            },            
        })
    }
    /**
     * 
     * @param {function} success (optional): A callback to execute on success. 
     * @param {function} failure (optional): A callback to execute on failure.
     * @param {boolean} relogin (optional): If False, do not attempt to automatically log in if the authentication is stale. Default is true.
     */
    getme(params){
        params.apipath = '/users/me/'; 
        console.log("getme called");
        console.log(params);
        this.apiget(params);
    }

    getMyProjects({success=null, author_only=true, include_components=false, error=ureAjaxError}){        
        this.local({
            url:'/osf/nodes', 
            params:{
                'bibliographic': author_only,
                'include_components': include_components,
            },
            success:success,
            error:error,
        });
    }

    registerLogin(me){
        var self = this;
        $('#osf-login').hide();
        $('#import-options').show();
        $('#osf-logout').show();
        $('.osf-login-required').each(function(){
            $(this).show();
        });
        $('.hide-after-login').each(function(){
            $(this).hide();
        });

        self.logged_in = true;
        console.log("In past attempts, the following would die with 'full_name: can't read properties on undefined' ")
        console.log("So what is it?")
        console.log(me);
        //debugger;

        if(me){
            // in this case, we logged in separately and are notifying the osf object of it, so we 
            // we don't need to call getme separately.
            self.me = me;
            $('#osf-authentication-status').html("Logged in as <b>" + me.attributes.full_name + "</b>.");
            self.loginCallbacks.forEach(function(callback){
                callback(me);
            });
        }
        else{
            // update the label and conduct any custom callbacks
            self.getme({success:function(me){            
                self.me = me;
                $('#osf-authentication-status').html("Logged in as <b>" + me.attributes.full_name + "</b>.");
                self.loginCallbacks.forEach(function(callback){
                    callback(me);
                });
            }});
        }
        console.log("Login complete");
        
    }

    registerLogout(){
        var self = this;
        $('#osf-login').show();
        $('#import-options').hide();
        $('#osf-logout').hide();
        $('#osf-authentication-status').html('');
        $('.osf-login-required').each(function(){
            $(this).hide();
        });
        $('.hide-after-login').each(function(){
            $(this).show();
        });

        this.logged_in = false;  
        self.me = null;      
        // update the label and conduct any custom callbacks
        self.logoutCallbacks.forEach(function(callback){
            callback();
        });
        console.log("Logout complete");
    }
    
    addLoginCallback(callback, initial_trigger=true){
        this.loginCallbacks.push(callback);
        if(this.logged_in && initial_trigger){
            callback(this.me);
        }
    }

    addLogoutCallback(callback, initial_trigger=true){
        this.logoutCallbacks.push(callback);
        if(!this.logged_in && initial_trigger){
            callback();
        }
    }
}

var osf = new OSFAuth();
$(document).ready(function () {

    //
    // Set the actions for hte login components
    //
    $('#osf-login').click(function(){            
        osf.launchAuthWindow();
    });
    
    $('#osf-logout').click(function(){
        osf.revokeCurrentToken();
    });

    //
    // Initialize based on current activity
    //
    $('#osf-login').show();
    $('#osf-logout').hide();
    $('#import-options').hide();
    osf.getme({
        success: function(me){osf.registerLogin(me)}, 
        error: function(){osf.registerLogout()},
        relogin: false,
    });
});
