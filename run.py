#!/usr/bin/env python3
import secrets, re, os, tempfile
import generate_table_page
from web_app import gen_plotters
from sites_parser.database import XlsDB
from sites_parser import tracker
from flask import Flask, render_template, request, redirect, session
from flask import send_file, abort

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CURRENT_DIR = os.getcwd()
XLS_DATABASES_OBJECTS_LIST = []

def check_allowed_symbols(name):
    if name and len(name) <= 40:
        match_res = re.match('[A-Za-z0-9_]+', name)
        if match_res and match_res.endpos == match_res.end():
            return True

    return False

def read_tmp_file(path):
    if type(path) is not str or not os.path.isfile(path):
        return ''

    with open(path, 'r', encoding='utf8') as tmp_fp:
        return tmp_fp.read()

    return ''

def show_databases():
    databases_dir = os.path.join(CURRENT_DIR, 'databases')
    db_list = []

    if os.path.isdir(databases_dir):
        for database in os.listdir(databases_dir):
            if '.xls' in database:
                db_list.append(database[:-4])

    return db_list

@app.route('/databases/<path:filename>')
def download(filename):
    if type(filename) is not str:
        abort(404)

    file_path = os.path.join(CURRENT_DIR, 'databases', filename)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)

    abort(404)

@app.route('/', methods=['GET', 'POST'])
def main_page():
    global XLS_DATABASES_OBJECTS_LIST
    categories_list = []
    monitor_products_list_left = []
    monitor_products_list_right = []
    databases_list = show_databases()
    database_filename = os.path.join(CURRENT_DIR, 'databases', '%s.xls')
    get_session_variable = lambda session_variable: \
            session[session_variable] if session_variable in session.keys() else ''
    
    if request.method == 'POST':
        values_dict = request.values.to_dict()
        print(request.values.to_dict())

        if 'db_name' in values_dict and \
                check_allowed_symbols(values_dict['db_name']):
            database_filename = database_filename % values_dict['db_name']
            if not os.path.isfile(database_filename):
                open(database_filename, 'w').close()

        if 'remove_db' in values_dict and \
                check_allowed_symbols(values_dict['remove_db']) and \
                get_session_variable('selected_db'):
            try:
                del session['selected_db']
                db_index = get_session_variable('database_object_index')
                if type(db_index) is int:
                    XLS_DATABASES_OBJECTS_LIST[db_index] = None

                database_filename = database_filename % values_dict['remove_db']
                os.remove(database_filename)
                session['category1'] = ''
                session['category2'] = ''
                databases_list = show_databases()

            except FileNotFoundError:
                pass

        if 'category_name' in values_dict and \
                check_allowed_symbols(values_dict['category_name']) and \
                get_session_variable('selected_db'):
            db_index = get_session_variable('database_object_index')

            if type(db_index) is int:
                if values_dict['category_name'] not in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                    XLS_DATABASES_OBJECTS_LIST[db_index].create_category_skel(values_dict['category_name'])

        if 'remove_category' in values_dict and \
                check_allowed_symbols(values_dict['remove_category']) and \
                get_session_variable('selected_db'):
            db_index = get_session_variable('database_object_index')
            rem_cat_name = values_dict['remove_category']

            if type(db_index) is int:
                XLS_DATABASES_OBJECTS_LIST[db_index].remove_category(rem_cat_name)

            if rem_cat_name == get_session_variable('category1'):
                session['category1'] = ''

            if rem_cat_name == get_session_variable('category2'):
                session['category2'] = ''

        if 'link_name' in values_dict and \
                get_session_variable('selected_db'):
            link = values_dict['link_name'].strip().replace('/www.', '/')
            find_res = re.findall('https://([\w\-]+.[\w]+)', link) 

            try:
                target_site = find_res[0]
                if target_site in tracker.SUPPORTED_SITES:
                    if 'add_link_left_cat' in values_dict.keys():
                        target_cat = get_session_variable('category1')
                    elif 'add_link_right_cat' in values_dict.keys():
                        target_cat = get_session_variable('category2')
                    else:
                        target_cat = ''

                    if target_cat:
                        db_index = get_session_variable('database_object_index')
                        if type(db_index) is int:
                            XLS_DATABASES_OBJECTS_LIST[db_index].add_link_to_category(
                                    target_cat,
                                    link,
                                    target_site
                            )

            except IndexError: # Name of site not found
                pass

        if ('sync_links_left_cat' in values_dict or 'sync_links_right_cat' in values_dict) and \
                get_session_variable('selected_db'):
            if 'sync_links_left_cat' in values_dict:
                target_cat = get_session_variable('category1')
            elif 'sync_links_right_cat' in values_dict:
                target_cat = get_session_variable('category2')
            else:
                target_cat = ''

            if target_cat:
                db_index = get_session_variable('database_object_index')
                if type(db_index) is int and \
                        target_cat in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                    products = XLS_DATABASES_OBJECTS_LIST[db_index].get_monitor_links_from_category(target_cat)
                    for product_dict_info in products:
                        try:
                            product_name, product_price = tracker.SHOPS_OBJECTS_DICTIONARY[product_dict_info['site']]().get_product_info(product_dict_info['link'])
                            XLS_DATABASES_OBJECTS_LIST[db_index].update_product_info(target_cat, product_dict_info['row'], product_name, product_price)
                        except (KeyError, TypeError): # TypeError if get_product_info return < 0
                            continue
        
        if ('plotter1' in values_dict or 'plotter2' in values_dict) and \
                get_session_variable('selected_db'):
            db_index = get_session_variable('database_object_index')

            if 'plotter1' in values_dict:
                cat_name = get_session_variable('category1')
                product_name = values_dict['plotter1']
                plot_file_path = 'plot1_file_path'
            else:
                cat_name = get_session_variable('category2')
                product_name = values_dict['plotter2']
                plot_file_path = 'plot2_file_path'
            
            if type(db_index) is int and cat_name:
                dates = XLS_DATABASES_OBJECTS_LIST[db_index].get_dates_from_category(cat_name)
                prices = XLS_DATABASES_OBJECTS_LIST[db_index].get_product_prices(cat_name, product_name)

                if len(dates) == len(prices) and dates and prices:
                    plotter = gen_plotters.Plotter()
                    for i in range(len(dates)):
                        if not prices[i] or not dates[i]:
                            continue
                        
                        try:
                            int(prices[i])
                        except ValueError: # prices[i] is str
                            continue

                        plotter.add_date_price(dates[i], prices[i])

                    plot_json = plotter.get_json_plot(product_name)

                    if plot_json:
                        tmp_file_fd_num, tmp_file_path = tempfile.mkstemp()
                        os.close(tmp_file_fd_num)
                        session[plot_file_path] = tmp_file_path

                        with open(session[plot_file_path], 'w') as plot_fp:
                            plot_fp.write(plot_json)

        if 'clear_plot1' in values_dict:
            if os.path.isfile(get_session_variable('plot1_file_path')):
                os.remove(session['plot1_file_path'])
                session['plot1_file_path'] = ''

        if 'clear_plot2' in values_dict:
            if os.path.isfile(get_session_variable('plot2_file_path')):
                os.remove(get_session_variable('plot2_file_path'))
                session['plot2_file_path'] = ''

        if 'show_left_links' in values_dict and \
            get_session_variable('selected_db') and \
            get_session_variable('category1'):
            db_index = get_session_variable('database_object_index')
            cat1 = get_session_variable('category1')

            if type(db_index) is int and type(cat1) is str:
                db_object = XLS_DATABASES_OBJECTS_LIST[db_index]
                return generate_table_page.generate_table(db_object, cat1, 'category1')

        if 'show_right_links' in values_dict and \
            get_session_variable('selected_db') and \
            get_session_variable('category2'):
            db_index = get_session_variable('database_object_index')
            cat2 = get_session_variable('category2')

            if type(db_index) is int and type(cat2) is str:
                db_object = XLS_DATABASES_OBJECTS_LIST[db_index]
                return generate_table_page.generate_table(db_object, cat2, 'category2')
        
        if 'delete_rows' in values_dict and \
            'from_category' in values_dict and \
            get_session_variable('selected_db'):
            cat = values_dict['from_category']
            if (cat == 'category1' or cat == 'category2') and get_session_variable(cat):
                db_index = get_session_variable('database_object_index')
                db_object = XLS_DATABASES_OBJECTS_LIST[db_index]
                from_cat = get_session_variable(cat)

                try:
                    delete_rows = list(map(int, values_dict['delete_rows'].split(',')))
                except ValueError:
                    pass

                for row in delete_rows:
                    db_object.delete_row(from_cat, row)

                db_object.sheet_compress(from_cat)
                
                return generate_table_page.generate_table(db_object, from_cat, cat)

        return redirect('/')

    elif request.method == 'GET':
        #print(dir(request.args))
        if 'selected_db' in request.args.keys() and \
                check_allowed_symbols(request.args.get('selected_db')):
            selected_db_arg = request.args.get('selected_db')

            try:
                if session['selected_db'] != selected_db_arg:
                    session['category1'] = ''
                    session['category2'] = ''
            except KeyError:
                pass

            database_filename = database_filename % selected_db_arg
            if os.path.isfile(database_filename):
                db_index = get_session_variable('database_object_index')
                if db_index == 0 or db_index:
                    XLS_DATABASES_OBJECTS_LIST[db_index] = XlsDB(db_filename=database_filename)
                else:
                    session['database_object_index'] = len(XLS_DATABASES_OBJECTS_LIST)
                    XLS_DATABASES_OBJECTS_LIST.append(XlsDB(db_filename=database_filename))

                session['selected_db'] = selected_db_arg
            else:
                session['selected_db'] = ''
                if not get_session_variable('database_object_index'):
                    session['database_object_index'] = None
                else:
                    XLS_DATABASES_OBJECTS_LIST[session['database_object_index']] = None
        
        if 'category1' in request.args.keys() and \
                check_allowed_symbols(request.args.get('category1')) and \
                get_session_variable('selected_db'):
            db_index = get_session_variable('database_object_index')
            cat1_arg = request.args.get('category1')

            if type(db_index) is int and cat1_arg in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                session['category1'] = cat1_arg
                monitor_products_list_left = XLS_DATABASES_OBJECTS_LIST[db_index].get_products_names_from_category(cat1_arg)
            else:
                session['category1'] = ''
        elif request.args.get('category1') == '':
            session['category1'] = ''
            
        if 'category2' in request.args.keys() and \
                check_allowed_symbols(request.args.get('category2')) and \
                get_session_variable('selected_db'):
            db_index = get_session_variable('database_object_index')
            cat2_arg = request.args.get('category2')

            if type(db_index) is int and cat2_arg in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                session['category2'] = cat2_arg
                monitor_products_list_right = XLS_DATABASES_OBJECTS_LIST[db_index].get_products_names_from_category(cat2_arg)
            else:
                session['category2'] = ''
        elif request.args.get('category2') == '':
            session['category2'] = ''

    db_index = get_session_variable('database_object_index')
    if type(db_index) is int and get_session_variable('selected_db'):
        try:
            categories_list = XLS_DATABASES_OBJECTS_LIST[db_index].get_categories()
        except AttributeError:
            categories_list = []

        cat1 = get_session_variable('category1')
        cat2 = get_session_variable('category2')

        if cat1:
            monitor_products_list_left = XLS_DATABASES_OBJECTS_LIST[db_index].get_products_names_from_category(cat1)

        if cat2:
            monitor_products_list_right = XLS_DATABASES_OBJECTS_LIST[db_index].get_products_names_from_category(cat2)

    #print(session)
    return render_template('index.html', \
            selected_db=get_session_variable('selected_db'), \
            selected_cat1=get_session_variable('category1'), \
            selected_cat2=get_session_variable('category2'), \
            databases_list=databases_list, \
            categories_list=categories_list, \
            supported_sites=tracker.SUPPORTED_SITES, \
            monitor_products_list_left=monitor_products_list_left, \
            monitor_products_list_right=monitor_products_list_right, \
            plotter1_json=read_tmp_file(get_session_variable('plot1_file_path')), \
            plotter2_json=read_tmp_file(get_session_variable('plot2_file_path'))
    )

if __name__ == '__main__':
    if not os.path.isdir('databases'):
        os.mkdir('databases')
    app.run(debug=True, host='0.0.0.0')
