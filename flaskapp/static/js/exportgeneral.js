
function export_to_osf(){
    $('#wait-dialog').dialog('open');
    osf.local({
        url: window.location.pathname, // the server handles posts as form input
        params: $('#project-export').serialize(),
        success: show_export_results,
        error: function(data){
            $('#wait-dialog').dialog("close");
            ureAjaxError(data);
        }
    });
}

function show_export_results(data){
    $('#wait-dialog').dialog("close");
    
    $('#result-header').html('<h1>Export Complete</h1><ul><li><a href="" onclick=\'$("#wait-dialog").dialog("close")\'>Click Here</a> to close this window and return to the exporter.</li><li><a href="http://osf.io/'+data.rootnodeid+'/">Click Here</a> to leave the exporter and go to the '+data.rootnodename+' Project.</li><li><a href="/">Click Here</a> to return to the URE Methods extensions index.</li></ul><p class="help-text">Below is a list of completed actions. Click on the links to open a <i>new window</i> for the page.</p><p>If you accidentally overwrote a wiki page, you can <b>revert</b> it to the old <b>Version</b> via the wiki page. If you accidentally deleted a wiki or component, it cannot be recovered.</p><p>' + data.markdown)

    //$('#result-message').html(div)
    $('#result-dialog').dialog('open');
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