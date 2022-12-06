$(document).ready(function () {
    $('#document-import')
        .submit(function(e){e.preventDefault()}) // disable default action
        .validate({
            ignore:[],
            errorClass: 'is-invalid',
            errorPlacement: function(error, element){
                var parent = element.parent();  
                error.addClass('invalid-feedback');                            
                parent.append(error);
                parent[0].scrollIntoView();                
            },
            submitHandler: import_to_osf,
            messages: {
                'osf-project-name': "Please select an OSF Project.",
                'osf-project-id': "Please re-select the project. Start typing and select the project *from the list* when it appears.",
                'fileid': "Please upload a Microsoft Word Document.", 
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
                'fileid': {
                    'required': true,
                    'minlength': 5,                    
                }
            }
        });
    
});