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