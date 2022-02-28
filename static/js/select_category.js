function select_category(cat_object)
{
    if ( cat_object.value && cat_object.id ) {
        var url = new URL(location.href);
        url.searchParams.set(cat_object.id, cat_object.value);
        location.href = url;
    }
}
