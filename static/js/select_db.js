function download_selected_db()
{
    var db_object = document.getElementById("selected_db");
    if ( db_object.value )
        window.open("/databases/" + db_object.value + ".xls");
    else
        alert("Database not selected");
}

function delete_selected_db()
{
    var db_object = document.getElementById("selected_db");
    if ( db_object.value ) {
        let del_db = confirm("Do you really want to delete database: " + db_object.value + "?");
        
        if ( del_db ) {
            var request_object = new XMLHttpRequest();
            request_object.open("POST", "/", true);
            request_object.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            request_object.send("remove_db" + "=" + db_object.value);
        }
    } else
        alert("Database not selected");
}

function send_selected_db()
{
    var db_object = document.getElementById("selected_db");
    var request_object = new XMLHttpRequest();
    if ( db_object.value && db_object.id ) {
        request_object.open("POST", "/", true);
        request_object.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        request_object.send(db_object.id + "=" + db_object.value);
    }
}
