#!/usr/bin/env python3
import random, re, os
from flask import Flask, render_template, request

app = Flask(__name__)
CURRENT_DIR = os.getcwd()

def check_names_db_cat(name):
    if name and len(name) <= 100:
        match_res = re.match('\w+', name)
        if match_res and match_res.endpos == match_res.end():
            return True

    return False

def show_databases():
    databases_dir = CURRENT_DIR + '/databases'
    db_list = []

    if os.path.isdir(databases_dir):
        for database in os.listdir(databases_dir):
            db_list.append(database)

    return db_list

@app.route('/', methods=['GET', 'POST'])
def main_page():
    info_message = ''
    databases_list = show_databases()

    if request.method == 'POST':
        values_dict = request.values.to_dict()
        if 'db_name' in values_dict:
            if check_names_db_cat(values_dict['db_name']):
                info_message = 'Database %s was created' % values_dict['db_name']
                ###################################### Create and define main database
            else:
                info_message = 'Error in database name: name may contain alphabet and numbers symbols. Also name length must be <= 100 symbols'

        #print(dir(request))
        #print(dir(request.values))
        #print(request.values.to_dict())
        #print(request.form.get('db_name'))
    return render_template('index.html', \
            title='Main', info_message=info_message, databases_list=databases_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
