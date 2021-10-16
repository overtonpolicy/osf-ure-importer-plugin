$(document).ready(function () {

    //
    // Set up the autocomplete
    //
    $('#google-document-name').autocomplete({
        minLength: 3,
        source: function(req, setData){
            $.ajax({
                url: "/google/getfiles",
                method: "POST",
                dataType: "json",
                data: {
                    'name_contains': req.term,
                    'all_drives': $('#google-include-shared').prop('checked'),
                },
                success: function(data) {                
                    if(data.error || data.errors)
                        ureAjaxError(data);
                    else if(data.result_count_exceeded){
                        return; // this happens when there are more than 50 results.  Keep typing, friends, keep typing.
                    }
                    else{
                        console.log("Google Files Search for " + req.term);
                        console.log(data);
                        var results = [];
                        data.forEach(function(fref){
                            results.push({value: fref.name, id: fref.id});
                        });
                        setData(results);
                    }
                },
                error: ureAjaxError
            });   
        },
        select: function(event, ui){
            // set the id to the hidden field            
            $('#google-document-id').val(ui.item.id);            
        }
    });

    //
    // Check to see if we're already authenticated
    //
    $('#document-import')
        .submit(function(e){e.preventDefault()}) // disable default action
        .validate({
            ignore:[],
            errorPlacement: function(error, element){
                var parent = element.parent();                
                parent.append(error);
                parent[0].scrollIntoView();                
            },
            submitHandler: import_to_osf,
            messages: {
                'osf-project-name': "Please select an OSF Project.",
                'osf-project-id': "Please re-select the project. Start typing and select the project <i>from the list</i> when it appears.",
                'google-document-name': "Please select a Google document.",
                'google-document-id': "Please re-select a Google document. start typing and select the document you want <i>from the list</i> when it appears.", 
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
                'google-document-id': {
                    'required':{
                        depends: function(element){
                            return($('#google-document-name').val());                            
                        }
                    },
                    'minlength': 5,
                },
                'google-document-name': {
                    'required': true,
                    'minlength': 3,                    
                }
            }
        });
});