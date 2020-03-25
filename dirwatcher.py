#!usr/bin/python3

__author__ = 'Rob Spears (GitHub: Forty9Unbeaten)'

import sys
import argparse

if sys.version_info[0] < 3:
    print('\n\tSincerest apologies, gotta use Python3\n')
    sys.exit()

# globals
exit_flag = False


def create_parser(args):
    '''Create and return a command-line argument parser'''
    parser = argparse.ArgumentParser(
        description='Monitors the creation of files with a specified ' +
        'extension and searches those files for a string of specified text',
        formatter_class=argparse.RawTextHelpFormatter,
        usage='%(prog)s [-h] [-i,--interval] ' +
        '[-t,--magictext][-l,--loglevel] dir ext')
    parser.add_argument('dir',
                        help='The directory to monitor')
    parser.add_argument('ext',
                        help='The file extension on which to filter')
    parser.add_argument('-i', '--interval',
                        help='polling interval (defaults to 1 second)',
                        metavar='',
                        dest='pollint')
    parser.add_argument('-t', '--text',
                        help='The string of text for which to monitor',
                        metavar='',
                        dest='text')
    parser.add_argument('-l', '--loglevel',
                        help='number that determines program log ' +
                        'verbosity\n\t1 - DEBUG (default)\n\t2 - INFO\n' +
                        '\t3 - WARNING\n\t4 - ERROR\n\t5 - CRITICAL',
                        metavar='',
                        dest='loglevel',
                        default=1)

    # print help if no args are supplied on command-line
    if not args:
        print('\n*** PLEASE SUPPLY THE PROPER ARGUMENTS. SEE HELP BELOW ***\n')
        parser.print_help()
        sys.exit()

    return parser


def main(args):
    parser = create_parser(args)
    ns = parser.parse_args()
    print(ns)


if __name__ == '__main__':
    main(sys.argv[1:])
