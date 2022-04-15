#!/usr/bin/env python3
import os
from optparse import OptionParser
from web_app import app

def main():
    parser = OptionParser()
    parser.add_option('-W', '--webapp', action='store_true', help='Run web application')
    (options, args) = parser.parse_args()

    if options.webapp:
        app.main_web_app(
                root_directory=os.getcwd(),
                databases_directory=os.path.join(os.getcwd(), 'databases')
        )

if __name__ == '__main__':
    main()
