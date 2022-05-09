#!/usr/bin/env python3
import os, sys
from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option('-W', '--webapp', action='store_true', help='Run web application')
    (options, args) = parser.parse_args()

    if options.webapp:
        os.chdir('web_app')
        sys.path.append(os.getcwd())
        from web_app import app
        app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
