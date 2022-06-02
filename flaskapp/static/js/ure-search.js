$(document).ready(function () {
    $('#search-results').DataTable({
        pageLength: 20,
        lengthMenu: [10,20,50,100],
        bLengthChange: false,
        language: {
            search: "Filter:"
        },
        pagingType: "simple",
    	responsive: true,
        "columns": [
            { 
                "width": "66%" ,
                "className": "article-link",
            },
            { 
                "width": "34%",
                "className": "article-authors",
            },
        ]
    });

    $('#search-button').click(conduct_search);
    $('#search-text').keypress(function(event) {    
        if (event.key === "Enter") {      
            event.preventDefault();
            $('#search-button').click();
        }
    });
});


function conduct_search(){
    var search_text = $('#search-text').val();
    if(!search_text.match(/\w/)){
        return;
    }
    $.ajax({
        type:'POST',
        url:'/search/conduct_search',
        data: {searchtext: search_text},
        dataType: 'json',
        error: function (d, s, x) {
            $('#error-message').html("<p><b>Error Status Code</b>: " + d.status + "</p><p><b>Error Text</b>: " + d.responseText + "</p>")
            $('#error-dialog').dialog("open");
        },
        success: function (data, status, jXHR) {
            if (data.error) {
                $('#error-message').html(data.error_messages[0]);
                $('#error-dialog').dialog("open");
                return;
            }
        var dt = $('#search-results').DataTable();
	    dt.clear();
	    dt.rows.add(data.results);
	    dt.draw();
	    //$('#search-results').DataTable({"data": data.results});
            console.log("search complete");
        },
    });
}

