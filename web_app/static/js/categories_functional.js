function select_category(cat_object)
{
    if ( cat_object.value && cat_object.id ) {
        var url = new URL(location.href);
        url.searchParams.set(cat_object.id, cat_object.value);
        location.href = url;
        return true;
    }
    return false;
}

function delete_cat(cat_number)
{
    if ( cat_number == 1 || cat_number == 2 ) {
        var cat_num_str = cat_number.toString();
        var cat_object = document.getElementById("category" + cat_num_str);
        var request_object = new XMLHttpRequest();
        request_object.open("POST", "/", true);
        request_object.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        request_object.send("remove_category" + "=" + cat_object.value);
        alert("Category " + cat_object.value + " was deleted");
        return true;
    }
    return false;
}
