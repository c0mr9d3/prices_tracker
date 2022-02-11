#!/usr/bin/env python3
import random
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('index.html', title='Main')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
