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
        * {background-color: aliceblue;}
        table, th, td {border:1px solid black;}
        header {
            display: flex;
            align-items: center;
            height: 40px;
            background-color: aqua;
        }
    </style>

    <header>
        <input type="button" value="&#8592" onclick="history.back();">
        Category's table: %s
    </header>
      <body>

      <table>
        <tr>
        <th><input onclick="modify_rows(%d, 1);" type="submit" value="Delete"></th>
        <th><input onclick="modify_rows(%d, 2)" type="submit" value="Monitor"></th>
        <th>Link</th>
        <th>Site</th>
        <th>Product name</th>
        </tr>
    ''' % (category, nrows, nrows)

    all_rows = []

    for row in range(1, nrows):
        monitor, link, site, name = db.get_row_info_slice(category, row)
        if monitor.strip() == '1':
            monitor = 'checked'
            all_rows.append('1')
        else:
            monitor = ''
            all_rows.append('0')

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

    all_rows = ','.join(all_rows)

    table_page += \
        '''
        </table>
        '''
    
    table_page += \
        '''
        <script>
            function check_changes_in_monitor(row, checked)
            {
                if ( !Number.isInteger(row) || !(typeof checked === "boolean") )
                    return false;

                var rows = [%s];

                if ( row < 1 || row > rows.length )
                    return false;

                row--;
                
                if ( (!checked && rows[row]) || (checked && !rows[row]) )
                    return true;

                return false;
            }

            function modify_rows(nrows, mode)
            {
                if ( !Number.isInteger(nrows) || !Number.isInteger(mode) )
                    return false;

                var prefix_id_name, mod_element, rows_joined, send_arg;
                var modify_rows = [];
                let answer;

                if ( mode == 1 ) {
                    answer = confirm("Are you sure want delete rows?");
                    
                    if ( !answer )
                        return false;

                    prefix_id_name = "del";
                    send_arg = "delete_rows";
                } else if ( mode == 2 ) {
                    answer = confirm("Are you sure want change monitor status for rows?");
                    
                    if ( !answer )
                        return false;

                    prefix_id_name = "monitor";
                    send_arg = "monitor_rows";
                } else {
                    return false;
                }

                for (var i = 1; i < nrows; i++) {
                    i_str = i.toString();
                    mod_element = document.getElementById(prefix_id_name + i_str);
                    checked = mod_element.checked;

                    if ( prefix_id_name === "del" && checked )
                        modify_rows.push(i_str);
                    else if ( prefix_id_name === "monitor" && check_changes_in_monitor(i, checked) ) {
                        modify_rows.push(i_str);
                    }
                }

                rows_joined = modify_rows.join();
                if ( answer && rows_joined ) {
                    var request_object = new XMLHttpRequest();
                    request_object.open("POST", "/", true);
                    request_object.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                    request_object.send(send_arg + "=" + rows_joined + "&from_category=%s");
                    location.reload(true);
                }
                return true;
            }
        </script>
        ''' % (all_rows, category_num)

    table_page += \
        '''
        </body>
        </html>
        '''

    return table_page
