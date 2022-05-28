/* This script expects entities that are defined in osf-project-select.html */

function updateProjectSelect(nodes) {

    // get the nodes
    var nodelist = [];    
    nodes.data.forEach(function (node) {

        // only for projects that the user is an author
        if (!node.attributes.current_user_is_contributor)
            return;

        // create the label (and list the parent project, if applicable)
        var label = node.attributes.title + ' [id: ' + node.id + ']';
        if (node.relationships.parent)
            label += " (component of " + node.relationships.parent.data.id + ")";

        nodelist.push({
            'id': node.id,
            'label': label,
            'desc': node.attributes.title + ': ' + node.attributes.category,
        });

    });

    // show the panel
    $('#osf-panel').show();

    $('#osf-project-name').prop('disabled', false);
    // set the autocomplete value
    $('#osf-project-name').autocomplete({
        source: nodelist,
        select: function (event, ui) {
            // set the id to the hidden field            
            $('#osf-project-id').val(ui.item.id);
        },
    });
    $('#osf-project-name').prop('placeholder', 'Start typing and select the target project.');
    $('#osf-project-fetch-info').html('<img src="/static/images/mcol_tick.png" height=20px style="vertical-align:middle"/>');
}

$(document).ready(function () {
    $('#osf-project-name').prop('disabled', true);

    osf.addLoginCallback(function(){
    	$('#osf-project-name').prop('disabled', true);
        
	osf.getMyProjects({success:updateProjectSelect});
    });
    
});
