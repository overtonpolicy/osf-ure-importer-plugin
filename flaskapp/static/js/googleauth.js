class GoogleAuth {

    /**
     * 
     * @param {array} scopes A list of google scopes to request
     */
    constructor(scopes){
        this.loginCallbacks = []
        this.logoutCallbacks = []
        this.logged_in = false 
        this.scopes = scopes;
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

        //create popup window for authorization
        var child = window.open(
            "/google/authenticate",
            'GoogleOauth',
            'width=550,height=700'
        );

        //listener to receive messages from child
        window.addEventListener(
            'message',
            function(event) {
                console.log("Google Message Received:");
                console.log(event);
                if(event.origin !== window.location.origin) 
                    return;

                if(event.data.authenticated){
                    child.postMessage('close', window.location.origin); 
                    self.completeAuthorization({success:params.success, error:params.error});                
                }
                else if (event.data.revoked){
                    child.postMessage('close', window.location.origin); 
                    if(error_callback)
                        error_callback();
                }
                else if(event.data.code){
                    // Note: this started to be noticed and received after initial development
                    // The code appears to be the access code, so I'm assuming it's just passed 
                    // along folowing a successful authentication
                    console.log('Code received, assuming log in successful and closing.') 
                    child.postMessage('close', window.location.origin); 
                    self.completeAuthorization({success:params.success, error:params.error});                
                }
                else{
                    console.warn("Not authenticated and not revoked");
                    console.log(event.data);
                    child.postMessage('close', window.location.origin); 
                    UREErrorDialog("Received a response from the child, but cannot comprehend it.")                    
                }
            },
            false,
        );
    }
    
    /** the function called by the authorization window to send the access code back to the parent*/
    static initializeCallback(){
        window.opener.postMessage(
            {'authenticated': true}, 
            window.location.origin,
        );
        window.close();
    }


    /** Completes the authorization by posting to the server to exchange the access code for an authorization token. */
    completeAuthorization(params){
        this.refreshLogin(params);
    }

    logout(params){
        var self = this;
        if(!params)
            params = {error:ureAjaxError};
        else if(!params.error)
            params.error = ureAjaxError;            

        $.ajax({
            url: "/google/logout",
            method: "POST",
            success: function(data) {    
                // we always register the logout because even if 
                // the token was already revoked, we need to hide the buttons.            
                self.registerLogout(data);
                if(data.error){
                    params.error(data);                     
                    if(params.on_error)
                        params.on_error(data);   
                }
                else if (data.errors){                    
                    params.error(data); 
                }
                else{
                    if(params.success)
                        params.success(data);
                }
            },
            error: params.error
        });
    }

    refreshLogin(params){
        var self = this;
        if(!params.error)
            params.error = ureAjaxError;            
        $.ajax({
            url: "/google/getme",
            method: "POST",
            dataType: "json",
            data: {},
            success: function(data) {                
                if(data.error){
                    params.error(data);                     
                    if(params.on_error)
                        params.on_error(data);   
                }
                else if (data.errors){                    
                    params.error(data); 
                }
                else{
                    if(!self.logged_in){
                        self.registerLogin(data);
                        if(params.success)
                            params.success(data);
                    }
                }
            },
            error: params.error
        });     
    }

    checkLogin(params){
        var self = this;
        if(!params)
            params = {error: ureAjaxError};
        if(!params.error)
            params.error = ureAjaxError;            

        $.ajax({
            url: "/google/getme",
            method: "POST",
            dataType: "json",
            data: {},
            success: function(data) {                
                if(data.error){
                    if(data.status_code == 401)
                        self.registerLogout(params);
                    else{
                        if(params.on_error)
                            params.on_error(data);   
                        params.error("Unkown error happened when trying to log in");
                    }
                }
                else{
                    self.registerLogin(data);
                }
            },
            error: params.error
        });     
    }

    registerLogin(me){
        var self = this;
        if(self.logged_in)
            return;
        $('#google-login').hide();
        $('#google-logout').show();
        $('.google-login-required').each(function(){
            $(this).show();
        });
        $('.hide-after-google-login').each(function(){
            $(this).hide();
        });
        self.logged_in = true;
        self.me = me;
        $('#google-authentication-status').html('You are logged in as ' + me.name);
        self.loginCallbacks.forEach(function(callback){
            callback(me);
        });
    }

    registerLogout(){
        var self = this;
        if(!self.logged_in)
            return;
        $('#google-login').show();
        $('#google-logout').hide();
        $('#google-authentication-status').html('You are not logged in.');
        $('.google-login-required').each(function(){
            $(this).hide();
        });
        $('.hide-after-google-login').each(function(){
            $(this).show();
        });

        self.logged_in = false;  
        self.me = null;      
        // update the label and conduct any custom callbacks
        self.logoutCallbacks.forEach(function(callback){
            callback();
        });
        console.log("Logout complete");
    }
}

var google = new GoogleAuth();
$(document).ready(function () {

    $('#google-login').click(function(){
        google.launchAuthWindow();
    });
    
    $('#google-logout').click(function(){
        google.logout();
    });

    // Initialize based on current activity
    $('#google-login').show();
    $('#google-logout').hide();
    $('.google-login-required').each(function(){
        $(this).hide();
    });
    google.checkLogin();
    //google.refreshLogin(success=function(me){google.registerLogin(me)} );
});
