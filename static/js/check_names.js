function check_name(name, target)
{
    let max_name_length = 40;

    if ( name ) {
        let result = name.match(/[0-9A-Za-z_]+/);

        if ( result && name.length <= max_name_length && result[0].length == name.length )
            alert(`${target} ` + result[0] + " was created.");
        else
            alert(`Error in ${target} name: name may contain only [0-9A-Za-z_] symbols. Also name length must be <= ${max_name_length} symbols`);
    }
}

function check_db_name(input_obj)
{
    if ( !input_obj.db_name.value )
        alert("Please, enter database name. Name should contain only [0-9A-Za-z_] symbols.");
    else
        check_name(input_obj.db_name.value, "database");
}

function check_category_name(input_obj)
{
    if ( !input_obj.category_name.value )
        alert("Please, enter category name. Name should contain only [0-9A-Za-z_] symbols.");
    else
        check_name(input_obj.category_name.value, "category");
}

