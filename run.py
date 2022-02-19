#!/usr/bin/env python3
import random, re, os
from sites_parser import tracker
from markupsafe import Markup
from flask import Flask, render_template, request, redirect
from flask import send_file, send_from_directory

app = Flask(__name__)
CURRENT_DIR = os.getcwd()

def check_names_db_cat(name):
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
    databases_list = show_databases()

    if request.method == 'POST':
        values_dict = request.values.to_dict()
        if 'db_name' in values_dict:
            if check_names_db_cat(values_dict['db_name']):
                filename = CURRENT_DIR + '/databases/' + values_dict['db_name'] + '.xls' 
                if not os.path.isfile(filename):
                    open(filename, 'w').close()

            return redirect('/')

        #print(request.values.to_dict())
        #print(request.form.get('db_name'))
    return render_template('index.html', \
            title='Main', databases_list=databases_list, supported_sites=tracker.SUPPORTED_SITES)

if __name__ == '__main__':
    if not os.path.isdir('databases'):
        os.mkdir('databases')
    app.run(debug=True, host='0.0.0.0')
