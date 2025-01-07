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


function import_to_osf(){
    var modaldiag = bootstrap.Modal.getInstance(document.getElementById('wait-dialog'));
    modaldiag.show();

    osf.local({
        url: window.location.pathname, // the server handles posts as form input
        params: $('#document-import').serialize(),
        success: show_import_results,
        error: function(data){
            bootstrap.Modal.getInstance(document.getElementById('wait-dialog')).hide();
            ureAjaxError(data);
        }
    });
}

function show_import_results(data){
    var modaldiag = bootstrap.Modal.getInstance(document.getElementById('wait-dialog'));
    modaldiag.hide();
    $('#result-header').html('Import Complete')
    $('#result-preamble').html('<p class="lead"><a href="" onclick=\'bootstrap.Modal.getInstance(document.getElementById("result-dialog")).hide()\'>Click Here</a> to close this window and return to the importer.</p><p class="lead"><a href="http://osf.io/'+data.rootnodeid+'/">Click Here</a> to leave the importer and go to the '+data.rootnodename+' Project.</p><p class="lead"><a href="/">Click Here</a> to return to the URE Methods extensions index.</p><p class="text-muted">Below is a list of completed actions. Click on the links to open a <i>new window</i> for the page.</p><p class="text-muted>If you accidentally overwrote a wiki page, you can <b>revert</b> it to the old <b>Version</b> via the wiki page. If you accidentally deleted a wiki or component, it cannot be recovered.</p>')
    var div = $('<div></div>');

    ['ignored', 'deleted', 'updated', 'created'].forEach(function(type){
        var actions = data.componentactions[type];
        if(actions && actions.length){
            div.append('<h2>Components ' + type[0].toUpperCase() + type.slice(1)+ '</h2>');
            var ul = div.append('<ul></ul>');
            actions.forEach(function(comp){
                var text = comp[1];
                if(comp.length >= 3) // Optional 3rd element is a message to append
                    text += '. <div class="help-text">'+comp[2]+'</div>'
                if(type == 'deleted') //no link
                    ul.append('<li>' + text + '</li>')
                else ul.append('<li><a href="http://osf.io/'+comp[0]+'/" target="_blank">' + text + '</a></li>')
            });
        }
    });

    ['ignored', 'deleted',  'updated', 'created'].forEach(function(type){
        var actions = data.wikiactions[type];
        if(actions && actions.length){
            div.append('<h4 class="mt-3">Wikis ' + type[0].toUpperCase() + type.slice(1)+ '</h4>');
            var ul = div.append('<ul></ul>')
            actions.forEach(function(comp){
                if(type == 'deleted')
                    ul.append('<li>' + comp[1] + ' from Node <a href="http://osf.io/'+comp[2]+'/" target="_blank">'+data.nodemap[comp[0]]+ '</li>')
                else ul.append('<li><a href="http://osf.io/'+comp[0]+'/wiki/'+encodeURIComponent(comp[1])+'/" target="_blank">' + comp[1] + '</a> from Node <a href="http://osf.io/'+comp[2]+'/" target="_blank">'+data.nodemap[comp[0]]+ '</li>')
            });
        }
    });
    $('#result-details').html(div)
    bootstrap.Modal.getInstance(document.getElementById('result-dialog')).show();
    console.log("Import complete")
}