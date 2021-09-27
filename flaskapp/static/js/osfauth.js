/** Class handling interactions with the OSF Api in javascript, using OAUTH2 by default. 
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
    completeAuthorization(on_success, on_error){
        var self = this;
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
                    if(on_success)
                        on_success(data);
                }
            },
            error: ureAjaxError
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
     * @param {function} success_callback - a function to be called if authorization is successful. If all is successful, this function will be called with the authorization token. If the call is valid but the server providdes an error, this function will be called with no parameters.
     * @param {function} error_callback - a function to be called if the ajax call fails.
     * 
     * TODO: Should success_callback really be called in cases of error? 
     */
    launchAuthWindow(success_callback, error_callback){
        var self = this;

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
                            self.completeAuthorization(success_callback, error_callback);
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
            error: ureAjaxError,    
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

    get(url, params, success, failure){
        if(!failure)
            failure = ureAjaxError;

        $.ajax({
            url: '/osf/get',
            method: 'POST',
            data: {
                url: url,
                params: params,
            },
            success: success,
            error: failure,            
        })
    }

    getme(success, failure=ureAjaxError){
        $.ajax({
            url: '/osf/me',
            method: 'POST',
            success: success,
            error: failure,            
        })
    }

    getMyProjects(callback, author_only=true, include_components=true, failure=ureAjaxError){        
        $.ajax({
            url: '/osf/nodes',
            method: 'POST',
            data: {
                'bibliographic': author_only,
                'include_components': include_components,
            },
            successs: callback,
            error: failure
        })
    }

    registerLogin(){
        var self = this;
        $('#osf-login').hide();
        $('#osf-logout').show();
        $('#osf-revoke').show();
        $('.osf-login-required').each(function(){
            $(this).show();
        });
        $('.hide-after-login').each(function(){
            $(this).hide();
        });

        this.logged_in = true;
        // update the label and conduct any custom callbacks
        this.getme(function(me){
            $('#osf-authentication-status').html('You are logged in as '+me.name+'.');
            self.loginCallbacks.forEach(function(callback){
                callback(me);
            });
        });
        console.log("Login complete");
        
    }

    registerLogout(){
        var self = this;
        $('#osf-login').show();
        $('#osf-logout').hide();
        $('#osf-revoke').hide();
        $('#osf-authentication-status').html('You are not logged in.');
        $('.osf-login-required').each(function(){
            $(this).hide();
        });
        $('.hide-after-login').each(function(){
            $(this).show();
        });

        this.logged_in = false;        
        // update the label and conduct any custom callbacks
        self.logoutCallbacks.forEach(function(callback){
            callback(me);
        });
        console.log("Logout complete");
    }
    
    addLoginCallback(callback, initial_trigger=true){
        this.loginCallbacks.push(callback);
        if(this.logged_in && initial_trigger){
            this.getme(callback);
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
        osf.launchAuthWindow(function(){osf.registerLogin()}, ureAjaxError);
    });
    
    $('#osf-logout').click(function(){
        osf.revokeCurrentToken(function(){osf.registerLogout()}, ureAjaxError);
    });

    $('#osf-revoke').click(function(){
        osf.revokeUserAuth(function(){osf.registerLogout()}, ureAjaxError);
    });

    //
    // Initialize based on current activity
    //
    //osf.getme( function(){osf.registerLogin()}, function(){osf.registerLogout()} );
});