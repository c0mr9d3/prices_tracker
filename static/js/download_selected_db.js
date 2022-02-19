function download_selected_db()
{
    var db_object = document.getElementById("selected_db");
    if ( db_object.value )
        window.open("/databases/" + db_object.value + ".xls");
    else
        alert("Database not selected");
}
