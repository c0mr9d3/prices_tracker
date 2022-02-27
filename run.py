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

        '''
        if 'selected_db' in values_dict and \
                check_allowed_symbols(values_dict['selected_db']):
            database_filename = database_filename % values_dict['selected_db']
            if os.path.isfile(database_filename):
                db_index = get_session_variable('database_object_index')
                if db_index == 0 or db_index:
                    XLS_DATABASES_OBJECTS_LIST[db_index] = database.XlsDB(db_filename=database_filename)
                else:
                    session['database_object_index'] = len(XLS_DATABASES_OBJECTS_LIST)
                    XLS_DATABASES_OBJECTS_LIST.append(database.XlsDB(db_filename=database_filename))

                session['selected_db'] = values_dict['selected_db']
            else:
                session['selected_db'] = ''
                if not get_session_variable('database_object_index'):
                    session['database_object_index'] = None
                else:
                    XLS_DATABASES_OBJECTS_LIST[session['database_object_index']] = None
        '''

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
                XLS_DATABASES_OBJECTS_LIST[db_index].create_category_skel(values_dict['category_name'])
        
        return redirect('/')

    elif request.method == 'GET':
        #print(request.args)
        if 'selected_db' in request.args.keys() and \
                check_allowed_symbols(request.args.get('selected_db')):
            database_filename = database_filename % request.args.get('selected_db')
            if os.path.isfile(database_filename):
                db_index = get_session_variable('database_object_index')
                if db_index == 0 or db_index:
                    XLS_DATABASES_OBJECTS_LIST[db_index] = database.XlsDB(db_filename=database_filename)
                else:
                    session['database_object_index'] = len(XLS_DATABASES_OBJECTS_LIST)
                    XLS_DATABASES_OBJECTS_LIST.append(database.XlsDB(db_filename=database_filename))

                session['selected_db'] = request.args.get('selected_db')
            else:
                session['selected_db'] = ''
                if not get_session_variable('database_object_index'):
                    session['database_object_index'] = None
                else:
                    XLS_DATABASES_OBJECTS_LIST[session['database_object_index']] = None

    db_index = get_session_variable('database_object_index')
    if db_index == 0 or db_index:
        try:
            categories_list = XLS_DATABASES_OBJECTS_LIST[db_index].get_categories()
        except AttributeError:
            categories_list = []
    
    return render_template('index.html', \
            title='Main', \
            selected_db=get_session_variable('selected_db'), \
            databases_list=databases_list, \
            categories_list=categories_list, \
            supported_sites=tracker.SUPPORTED_SITES)

if __name__ == '__main__':
    if not os.path.isdir('databases'):
        os.mkdir('databases')
    app.run(debug=True, host='0.0.0.0')
