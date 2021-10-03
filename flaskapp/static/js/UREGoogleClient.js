var GoogleAuth;

function handleClientLoad() {
    // Load the API's client and auth2 modules.
    // Call the initClient function after the modules load.
    gapi.load('client:auth2', initClient);
}

function initClient() {

    // Initialize the gapi.client object, which app uses to make API requests.
    // This requires client information which can change over time and is rendered by an internal endpoint. 

    // Get API key and client ID from API Console.
    // 'scope' field specifies space-delimited list of access scopes.
    $.ajax({
        url: "/auth/googleclient",
        method: "POST",
        dataType: "json",
        data: {context: 'read_docs'},
        error: ureAjaxError,
        success: function(gapi_params){

            gapi.client.init(gapi_params).then(function () {
                GoogleAuth = gapi.auth2.getAuthInstance();

                // Listen for sign-in state changes.
                GoogleAuth.isSignedIn.listen(updateSigninStatus);

                // Handle initial sign-in state. (Determine if user is already signed in.)
                var user = GoogleAuth.currentUser.get();
                setSigninStatus(gapi_params.scope);

                // Call handleAuthClick function when user clicks on
                //      "Sign In/Authorize" button.
                $('#google-login').click(function () {
                    handleAuthClick();
                });
                $('#google-revoke').click(function () {
                    revokeAccess();
                });
            });
        }
    });
}

function handleAuthClick() {
    if (GoogleAuth.isSignedIn.get()) {
        // User is authorized and has clicked "Sign out" button.
        GoogleAuth.signOut();
    } else {
        // User is not signed in. Start Google auth flow.
        GoogleAuth.signIn();
    }
}

function revokeAccess() {
    GoogleAuth.disconnect();
}

function setSigninStatus(scopes) {
    var user = GoogleAuth.currentUser.get();
    var isAuthorized = user.hasGrantedScopes(scopes);
    if (isAuthorized) {
        $('#google-login').html('Sign out');
        $('#google-panel').css('display', 'inline-block');
        $('#google-revoke').css('display', 'inline-block');
    } else {
        $('#google-login').html('Sign In/Authorize');
        $('#google-panel').css('display', 'none');
        $('#google-revoke').css('display', 'none');
    }
}


// Load the API and make an API call.  Display the results on the screen.
function makeApiCall() {
    console.log("Making api call");
    var request = gapi.client.drive.files.get({
        'fileId': '1w3P2h9VvRG9PDePrr7DA56wILRUoez9ndX6mvUtevqk'
      });
      
      request.execute(function(resp) {
          debugger; 
        console.log('Title: ' + resp.name);
        console.log('Description: ' + resp.description);
        console.log('MIME type: ' + resp.mimeType);
      });
      
    
    console.log("Finished with call");   
    return(false); 
}

// List the documents given the partial string 
function listDocs(search_string) {
    if(!search_string)
        search_string = 'Exper';

    console.log("SS: " + search_string);
    
    var request = gapi.client.drive.files.list({'q': 'name contains "Exper"'});
    
    //request.setQ('title contains "Exper"');
    //q:"title contains 'Exper'"
    
    
    //var request = gapi.client.drive.files.list().setQ("title contains '"+search_string+"'");
        //q:"title contains '"+search_string+"'",
    //});
    
       //.setQ("mimeType='application/vnd.google-apps.document',title contains '"+search_string+"'");
//        .setOrderBy('modifiedByMeDate');
              
      request.execute(function(resp) {
          debugger; 
          console.log(resp);
      });
      
    
    console.log("Finished with call");   
    return(false); 
}


function updateSigninStatus() {
    setSigninStatus();
}

$(document).ready(function () {

    //
    // Gooogle Login button
    //
    handleClientLoad();

    //
    // Set the Google Document search box as an ajax-autocomplete 
    // To fetch data as it is typed. On select, set the hidden id 
    $('#google-document-name').autocomplete({
        minLength: 3,
        source: function(req, setData){
            var request = gapi.client.drive.files.list({'q': 'name contains "'+req.term+'" and mimeType="application/vnd.google-apps.document"'});
            request.execute(function(resp) {
                console.log(resp);
                var results = [];
                resp.files.forEach(function(f){
                    results.push({value: f.name, id: f.id});
                });
                setData(results);
            });             
        },
        select: function(event, ui){
            // set the id to the hidden field            
            $('#google-document-id').val(ui.item.id);            
        }
    });
});
