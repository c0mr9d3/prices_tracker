def generate_table(db, category, category_num):
    if type(category) is not str or category not in db.get_categories():
        return '<html>Wrong category_name</html>'

    nrows = db.get_category_nrows(category)
    if not nrows or nrows < 2:
        return '<html>Products rows not found</html>'

    if category_num != 'category1' and category_num != 'category2':
        return '<html>Wrong category number</html>'

    table_page = \
    '''
    <!DOCTYPE html>
    <html>
    <style>
        table, th, td {border:1px solid black;}
    </style>

    <head>
    Category's table: %s
    </head>
      <body>

      <table>
        <tr>
        <th><input onclick="delete_rows(%d);" type="submit" value="Delete"></th>
        <th><input type="submit" value="Monitor"></th>
        <th>Link</th>
        <th>Site</th>
        <th>Product name</th>
        </tr>
    ''' % (category, nrows)

    for row in range(1, nrows):
        monitor, link, site, name = db.get_row_info_slice(category, row)
        if monitor.strip() == '1':
            monitor = 'checked'
        else:
            monitor = ''

        table_page += \
        '''
        <tr>
        <td><input type="checkbox" id="del{row}"></td>
        <td><input type="checkbox" id="monitor{row}" {checked}></td>
        <td><a href="{link}">link</a></td>
        <td><a href="https://{site}">{site}</a></td>
        <td>{name}</td>
        </tr>
        '''.format(row=row, link=link, site=site, name=name, checked=monitor)

    table_page += \
        '''
        </table>
        '''
    
    table_page += \
        '''
        <script>
            function delete_rows(nrows)
            {
                if ( !Number.isInteger(nrows) )
                    return false;

                var rows_del = [];
                var del_element, rows_joined;

                for (var i = 1; i < nrows; i++) {
                    i_str = i.toString();
                    del_element = document.getElementById("del" + i_str);

                    if ( del_element.checked )
                        rows_del.push(i_str);
                }

                rows_joined = rows_del.join()
                if ( rows_joined ) {
                    var request_object = new XMLHttpRequest();
                    request_object.open("POST", "/", true);
                    request_object.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                    request_object.send("delete_rows" + "=" + rows_joined + "&from_category=%s");
                    location.reload(true);
                }
                return true;
            }
        </script>
        ''' % category_num

    table_page += \
        '''
        </body>
        </html>
        '''

    return table_page
