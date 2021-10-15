$(document).ready(function () {

    // Dialog-ify all the dialogs - automatically adds a message div.
    $('.response-dialog').each(function(){
        var diag = jQuery(this);
        
        var buttons;
        if(!diag.hasClass('no-buttons'))
            buttons = [{ text: "Ok", click: function() { $( this ).dialog( "close" );} }];
        
        var width = diag.attr("width");
        if(!width)
            width = 700;
        
        diag.append('<div class="message"></div>');
        diag.dialog({
            autoOpen: false,
            modal: true,
            width: width,
            buttons: buttons,
        });
    });

    // anything with form-options group should be accordian-ized
    $('.form-options').each(function(){
        var optgroup = jQuery(this);
        var is_active = true;
        if(optgroup.attr("closed")){
            cl = 'ui-accordion-header-collapsed';        
        }
        else{
            cl = 'ui-accordion-header-active';        
        }
        console.log("Is Active", is_active)
        optgroup.accordion({
            'collapsible':true,
            //'active': null,
            'classes': cl,
        });
    });

});


/** A shorthand to render errors in a dialog. It is expected that there is a DIV/dialog withh id 'error-dialog' and a div/span inside it with id 'error-message' that gets the details of any error.
 * 
 * @param {string|array} error_message - The message(s) to display.
 */
 function UREErrorDialog(error_message){

    var errdiag = $('#error-dialog');
    
    if(!errdiag){
        alert(error_message);
        return;
    }
    var msgdiv = errdiag.find('.message');
    if(typeof(error_message) == 'array'){
        msgdiv.html(data.error_message[0].detail);
    }
    else{
        msgdiv.html(error_message);
    }
    errdiag.dialog('open');
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
    //debugger;
    UREErrorDialog(messages);
}

