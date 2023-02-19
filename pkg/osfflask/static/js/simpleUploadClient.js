$(document).ready(function () {
    //
    // This implements the simpleUpload for any elements with the simple-upload class.
    // Later, this this be genericized and templated so to allow for a variety of extensions from flask
    // Useful plugin from Michael C. Brooks: https://simpleupload.michaelcbrook.com/
    //
    //
    
    $('.simple-upload').change(function(){
        var fileinput = jQuery(this);
        fileinput.simpleUpload(
        "/import/process_docx_upload",
        {
            allowedExts: ['docx', 'DOCX'],
            start: function(file){ 
                console.log("DEBUG: simpleUpload file upload begun. "); console.log(file); 
                $('#filename').html(file.name);
                $('#upload-progress').width(0);
                $('#upload-status').html('Uploading');
            },
            progress: function(progress){ console.log(
                "DEBUG: simpleUpload upload progress: " +  progress); 

                $('#upload-status').html('Uploading ( '+Math.round(progress)+'% complete)');
                $('#upload-progress').width(progress + '%');
            },
            success: function(data){ 
                console.log("DEBUG: simpleUpload file upload complete!. "); console.log(data); 
                $('#upload-status').html('Uploaded!');
                $('#upload-progress').width('100%');
                $('#fileid').val(data.id);

            },
            error: function(err){ 
                
                $('#filename').html('none');
                $('#upload-progress').width(0);
                $('#upload-status').html('Failed: '+ err.name +": " + err.message);

                alert("simpleUpload file upload error: " + err.name +": " + err.message); 
            },
            //dropZone: '#docx-drop-zone',
            //progress: '#docx-progress',
        });
    });
});
