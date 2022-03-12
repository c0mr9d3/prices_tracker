#!/usr/bin/env python3
import random, re, os, time
from sites_parser import tracker, database
from markupsafe import Markup
from flask import Flask, render_template, request, redirect, session
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = str(time.time())

CURRENT_DIR = os.getcwd()
XLS_DATABASES_OBJECTS_LIST = []

def check_allowed_symbols(name):
    if name and len(name) <= 40:
        match_res = re.match('\w+', name)
        if match_res and match_res.endpos == match_res.end():
            return True

    return False

def show_databases():
    databases_dir = CURRENT_DIR + '/databases'
    db_list = []

    if os.path.isdir(databases_dir):
        for database in os.listdir(databases_dir):
            if '.xls' in database:
                db_list.append(database[:-4])

    return db_list

@app.route('/databases/<path:filename>')
def download(filename):
    return send_from_directory(path=CURRENT_DIR, directory='databases/', filename=filename)

@app.route('/', methods=['GET', 'POST'])
def main_page():
    global XLS_DATABASES_OBJECTS_LIST
    categories_list = []
    databases_list = show_databases()
    database_filename = CURRENT_DIR + '/databases/' + '%s.xls'
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
                check_allowed_symbols(values_dict['remove_db']):
            try:
                del session['selected_db']
                db_index = get_session_variable('database_object_index')
                if db_index == 0 or db_index:
                    XLS_DATABASES_OBJECTS_LIST[db_index] = None

                database_filename = database_filename % values_dict['remove_db']
                os.remove(database_filename)
                databases_list = show_databases()

            except FileNotFoundError:
                pass

        if 'category_name' in values_dict and \
                check_allowed_symbols(values_dict['category_name']):
            db_index = get_session_variable('database_object_index')

            if db_index == 0 or db_index:
                if values_dict['category_name'] not in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                    XLS_DATABASES_OBJECTS_LIST[db_index].create_category_skel(values_dict['category_name'])

        if 'remove_category' in values_dict and \
                check_allowed_symbols(values_dict['remove_category']) and \
                get_session_variable('selected_db'):
            db_index = get_session_variable('database_object_index')
            rem_cat_name = values_dict['remove_category']

            if db_index == 0 or db_index:
                XLS_DATABASES_OBJECTS_LIST[db_index].remove_category(rem_cat_name)

        if 'link_name' in values_dict:
            link = values_dict['link_name'].strip().replace('/www.', '/')
            find_res = re.findall('https://([\w\-]+.[\w]+)', link) 

            try:
                target_site = find_res[0]
                if target_site in tracker.SUPPORTED_SITES and get_session_variable('selected_db'):
                    if 'add_link_left_cat' in values_dict.keys() and get_session_variable('category1'):
                        db_index = get_session_variable('database_object_index')
                        #XLS_DATABASES_OBJECTS_LIST[db_index].add_info(
                        #    category=get_session_variable('category1'),
                        #    shop=target_site,
                        #    product_name=,
                        #    price=,
                        #    product_link=link
                        #)
                    elif 'add_link_right_cat' in values_dict.keys() and get_session_variable('category2'):
                        print(get_session_variable('category2'))

            except IndexError: # Name of site not found
                pass
        
        return redirect('/')

    elif request.method == 'GET':
        #print(request.args)
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
                    XLS_DATABASES_OBJECTS_LIST[db_index] = database.XlsDB(db_filename=database_filename)
                else:
                    session['database_object_index'] = len(XLS_DATABASES_OBJECTS_LIST)
                    XLS_DATABASES_OBJECTS_LIST.append(database.XlsDB(db_filename=database_filename))

                session['selected_db'] = selected_db_arg
            else:
                session['selected_db'] = ''
                if not get_session_variable('database_object_index'):
                    session['database_object_index'] = None
                else:
                    XLS_DATABASES_OBJECTS_LIST[session['database_object_index']] = None

        
        if 'category1' in request.args.keys() and \
                check_allowed_symbols(request.args.get('category1')):
            db_index = get_session_variable('database_object_index')
            cat1_arg = request.args.get('category1')

            if (db_index == 0 or db_index) and cat1_arg in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                session['category1'] = cat1_arg
            else:
                session['category1'] = ''
        elif request.args.get('category1') == '':
            session['category1'] = ''
            
        if 'category2' in request.args.keys() and \
                check_allowed_symbols(request.args.get('category2')):
            db_index = get_session_variable('database_object_index')
            cat2_arg = request.args.get('category2')

            if (db_index == 0 or db_index) and cat2_arg in XLS_DATABASES_OBJECTS_LIST[db_index].get_categories():
                session['category2'] = cat2_arg
            else:
                session['category2'] = ''
        elif request.args.get('category2') == '':
            session['category2'] = ''

    db_index = get_session_variable('database_object_index')
    if db_index == 0 or db_index:
        try:
            categories_list = XLS_DATABASES_OBJECTS_LIST[db_index].get_categories()
        except AttributeError:
            categories_list = []
    
    #print(session)
    return render_template('index.html', \
            title='Main', \
            selected_db=get_session_variable('selected_db'), \
            selected_cat1=get_session_variable('category1'), \
            selected_cat2=get_session_variable('category2'), \
            databases_list=databases_list, \
            categories_list=categories_list, \
            supported_sites=tracker.SUPPORTED_SITES)

if __name__ == '__main__':
    if not os.path.isdir('databases'):
        os.mkdir('databases')
    app.run(debug=True, host='0.0.0.0')
