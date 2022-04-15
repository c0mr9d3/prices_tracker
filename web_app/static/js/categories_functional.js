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
    if ( cat_number === 1 || cat_number === 2 ) {
        var cat_num_str = cat_number.toString();
        var cat_object = document.getElementById("category" + cat_num_str);
        var cat_str = cat_object.value.toString();

        if ( !cat_object )
            return false;

        let del_cat = confirm(`Do you really want to delete category ${cat_str}?`);

        if ( del_cat ) {
            var request_object = new XMLHttpRequest();
            request_object.open("POST", "/", true);
            request_object.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            request_object.send("remove_category" + "=" + cat_str);
            alert("Category " + cat_str + " was deleted");
            return true;
        }
    }
    return false;
}
