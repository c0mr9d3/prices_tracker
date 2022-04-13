#!/usr/bin/env python3
from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.add_option('-W', '--webapp', action='store_true', help='Run web application')
    (options, args) = parser.parse_args()

    if options.webapp:
        print('WEBAPP')

if __name__ == '__main__':
    main()
