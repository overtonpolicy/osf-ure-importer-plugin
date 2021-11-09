
function show_export_results(data, status, jqXHR){
    $('#wait-dialog').dialog("close");
    $('#result-header').html('<h1>Export Complete</h1><ul><li><a href="" onclick=\'$("#wait-dialog").dialog("close")\'>Click Here</a> to close this window and return to the exporter.</li><li><a href="http://osf.io/'+$('#osf-project-id').val()+'/">Click Here</a> to leave the exporter and go to the '+$('#osf-project-name').val()+' Project.</li><li><a href="/">Click Here</a> to return to the URE Methods extensions index.</li></ul>')

    //$('#result-message').html(div)
    $('#result-dialog').dialog('open');
    var disposition = jqXHR.getResponseHeader('Content-Disposition');
    var filename;
    if (disposition && disposition.indexOf('attachment') !== -1) {
        var filenameRegex = /filename[^;=\n]*=['"](.*?\2|[^;\n]*\.docx)['"]/i;
        var matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) 
            filename = matches[1];
    }

    if(!filename){
        filename = "untitled.docx";
    }
    var URL = window.URL || window.webkitURL;
    var downloadUrl = URL.createObjectURL(data, {type:jqXHR.getResponseHeader('Content-Type')});

    // use HTML5 a[download] attribute to specify filename

    var a = document.createElement("a");
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup data from webpage
}


function export_to_osf(){ 
    $('#wait-dialog').dialog('open');
    $.ajax({
        url: window.location.pathname, // the server handles posts as form input
        data: $('#project-export').serialize(),
        method: 'POST',
        error: function(d,s,x){ $('#wait-dialog').dialog('close'); ureAjaxError(d,s,x)},            
        success: show_export_results,
        processData: 'false',
        responseType: 'blob',
        xhrFields: {
            responseType: 'blob' // to avoid binary data being mangled on charset conversion
        },
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
}


$(document).ready(function () {
    $('#project-export')
        .submit(function(e){e.preventDefault()}) // disable default action
        .validate({
            ignore:[],
            errorPlacement: function(error, element){
                var parent = element.parent();                
                parent.append(error);
                parent[0].scrollIntoView();                
            },
            submitHandler: export_to_osf,
            messages: {
                'osf-project-name': "Please select an OSF Project.",
                'osf-project-id': "Please re-select the project. Start typing and select the project *from the list* when it appears.",
            },
            rules: {
                'osf-project-name': {
                    'required':true,
                    'minlength': 3,
                },
                'osf-project-id': {
                    'required':{
                        depends: function(element){
                            return($('#osf-project-name').val());                            
                        }
                    },
                    'minlength': 4,
                },
            }
        });
    
});