/**

Copyright (c) 2024, Kevin Crouse. 

This file is part of the *URE Methods Plugin Repository*, located at 
https://github.com/kcphila/osf-ure-plugins

This file is distributed under the terms of the GNU General Public License 3.0
and can be used, shared, or modified provided you attribute the original work 
to the original author, Kevin Crouse.

See the README.md in the root of the project directory, or go to 
http://www.gnu.org/licenses/gpl-3.0.html for license details.

*/

$(document).ready(function () {
    $('.modal').each(function(){
        var modal = new bootstrap.Modal(this);
    });
});

function showWait(){
    bootstrap.Modal.getInstance(document.getElementById('wait-dialog')).show();
}

function hideWait(){
    bootstrap.Modal.getInstance(document.getElementById('wait-dialog')).hide();
}


/** A shorthand to render errors in a dialog. It is expected that there is a DIV/dialog withh id 'error-dialog' and a div/span inside it with id 'error-message' that gets the details of any error.
 * 
 * @param {string|array} error_message - The message(s) to display.
 */
 function UREErrorDialog(error_message){
    var errdiag = document.getElementById('error-dialog');
    
    if(!errdiag){
        alert(error_message);
        return;
    }
    var msgdiv = $('#error-message');
    var messagehtml = '<div class="lead">';
    if(typeof(error_message) == 'array')
        messagehtml += error_message[0].detail;
    else
        messagehtml += error_message;
    messagehtml += "</div>";

    messagehtml += '<div class="text-muted mt-4">If you believe this error is a problem and needs attention, please report it to the <a href="mailto:kevin@uremethods.org">URE Methods tech support team.</div>';

    msgdiv.html(messagehtml);
    
    var modaldiag = new bootstrap.Modal(errdiag);
    modaldiag.show();
}


/**
 * A generic function that can be added as the failure response for any ajax call - really just processes the data and deleges to the error dialog.
 */
 function ureAjaxError(data, status, xhr){
    var messages;
    if(typeof(data) == "string")
        messages = data;
    if(data.responseText)
        messages = data.responseText;
    else if(data.statusText && data.status){
        messages = "<div>Server returned status code " + data.status + ": " + data.statusText + "</div>";
        if(data.status == 400){
            messages += "<div class='text-muted'>Sometimes the service providers will time out or log you out of your account on the remote end, leading to this error. If this error has only happened once, please Log out of OSF any other services and try again</div>" 
        }
    }
    else if(data.errors){
        messages = [];
        data.errors.forEach(function(err){
            if(typeof(err) == 'string')
                messages.push(err);
            else
                messages.push(err.detail);
        })
    }
    else if(data.error_message)
        messages = data.error_message;
    else if(data.error_description)
        messages = data.error_description;
    else if(data.message)
        messages = data.message;
    else if(data.error)
        messages = data.error;
    UREErrorDialog(messages);
}

