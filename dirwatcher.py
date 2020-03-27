#!usr/bin/python3

__author__ = 'Rob Spears (GitHub: Forty9Unbeaten)'

import sys
import argparse
import logging
from datetime import datetime as dt
import os
import textwrap
import signal
import re
import time

if sys.version_info[0] < 3:
    print('\n\tSincerest apologies, gotta use Python3\n')
    sys.exit()

# globals
exit_flag = False
logger = logging.getLogger(__file__)


def create_parser(args):
    '''
    Create and return a command-line argument parser

    Parameters:

    args: Arguments present and given via the command-line

    Return: An ArgumentParser instance
    '''
    parser = argparse.ArgumentParser(
        description='Monitors the creation of files with a specified ' +
        'extension and searches those files for a string of specified text',
        formatter_class=argparse.RawTextHelpFormatter,
        usage='%(prog)s [-h] [-i,--interval] ' +
        '[-l,--loglevel] dir ext text')
    parser.add_argument('dir',
                        help='The directory to monitor')
    parser.add_argument('ext',
                        help='The file extension on which to filter')
    parser.add_argument('text',
                        help='The string of text for which to monitor',)
    parser.add_argument('-i', '--interval',
                        help='polling interval (defaults to 1 second)',
                        metavar='',
                        dest='pollint',
                        type=float,
                        default=1.0)
    parser.add_argument('-l', '--loglevel',
                        help='number that determines program log ' +
                        'verbosity\n\t1 - DEBUG\n\t2 - INFO (default)\n' +
                        '\t3 - WARNING\n\t4 - ERROR\n\t5 - CRITICAL',
                        metavar='',
                        dest='loglevel',
                        default=2)

    # print help if no args are supplied on command-line
    if not args:
        print('\n*** PLEASE SUPPLY THE PROPER ARGUMENTS. SEE HELP BELOW ***\n')
        parser.print_help()
        sys.exit()

    return parser


def set_log_level(log_code):
    '''
    Takes log level code as argument and returns log level
    to be used for logger instantiation

    Parameters:

    log_code: the integer code supplied as an arg on the command-line

    Return: The log level to be supplied to a new logger instance
    '''
    log_levels = {
        '1': logging.DEBUG,
        '2': logging.INFO,
        '3': logging.WARNING,
        '4': logging.ERROR,
        '5': logging.CRITICAL
    }
    try:
        return log_levels[str(log_code)]
    except KeyError:
        return log_levels['1']
    except Exception:
        raise


def config_logger(log_level):
    '''
    Configure the logger instance with a level of log_level

    Parameters:

    log_level: the level at which the log should be reporting/outputting

    Return: None
    '''

    # formatting variables
    log_format = '%(asctime)s |%(levelname)s| func: %(funcName)s ' +\
        '| line: %(lineno)d | %(message)s'
    log_date_format = '%b %d, %Y <%I:%M:%S %p>'

    logging.basicConfig(
        format=log_format,
        datefmt=log_date_format,
        level=log_level)


def config_signal_handlers():
    '''
    Attach handlers to various OS signals that the program may receive

    Parameters: None

    Return: None
    '''
    signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]
    for sig in signals:
        signal.signal(sig, signal_handler)
        logger.debug('{} signal handler connected'.format(
            signal.Signals(sig).name))
    logger.info('All signal handlers connected')


def signal_handler(sig_num, frame):
    '''
    A handler for various signals. THe main() function will loop
    indefinitely until the signal is received by this function

    Parameters:

    sig_num: The integer code of the signal received by the OS
    frame: unused

    Return:
    None
    '''
    logger.warning('Received {}'.format(signal.Signals(sig_num).name))
    global exit_flag
    exit_flag = True


def watch_directory(directory, file_ext, magic_text, interval):
    '''
    Monitor files in a specific directory for a specific string of text

    Parameters:

    directory: The directory to monitor
    file_ext: extension of the files in which to look for text string
    magic_text: the string of text for which to look
    interval: the rate at which the function looks in the directory
    files for the text

    Return: None
    '''
    # regular expression to isolate files with specified extension
    extension_regex = r'\S*{}\Z'.format(file_ext)

    # dictionary that tracks files that have been read
    # keys are filenames and values are number of lines already read
    file_cache = {}

    directory_path = os.path.abspath(directory)
    logger.info('Monitored Directory: {}, File Ext: {},'.format(directory_path,
                                                                file_ext)
                + ' Text: {}, Interval: {}'.format(magic_text, interval))

    while not exit_flag:
        try:
            # construct list of paths to files with the appropriate extension
            logger.debug('Getting files with {} extension in {}'.format(
                file_ext, directory_path))
            files = ['{}/{}'.format(directory_path, file) for file in
                     os.listdir(directory_path) if
                     re.search(extension_regex, file)]

            # add and remove appropriate files from cache dictionary
            logger.debug(
                'Checking for new files in {}'.format(directory_path))
            file_cache = sync_added_files(file_cache, files)
            logger.debug(
                'Checking for deleted files in {}'.format(directory_path))
            file_cache = sync_deleted_files(file_cache, files)

            if files:
                # read files in directory, accounting for lines that
                # have already been read
                for file in files:
                    logger.debug('Reading file {}'.format(
                        os.path.basename(file)))
                    start_line = file_cache[file]
                    new_content = read_single_file(file, start_line)
                    # if new data has been read from file, search it
                    # for the magic text
                    if new_content:
                        logger.debug(
                            'Checking newly read lines for the magic text')
                        magic_text_lines = check_magic_text(
                            new_content, magic_text, start_line)
                        # if there are any lines that have the magic_text,
                        # log the matches
                        if magic_text_lines:
                            logger.debug('Reporting lines in files that ' +
                                         'contain magic text')
                            for i in range(len(magic_text_lines)):
                                logger.info(
                                    '"{}" found in file {} on line {}'.format(
                                        magic_text,
                                        os.path.basename(file),
                                        magic_text_lines[i]
                                    )
                                )
                        # update the cache dictionary to reflect the new lines
                        # that have been read
                        logger.debug('Updating cache dictionary to ' +
                                     'account for lines that have been read')
                        file_cache[file] += len(new_content)
            else:
                # no files with specified extension in the directory
                logger.debug('No files with {} extension in {}'.format(
                    file_ext, directory_path))
        except FileNotFoundError:
            logger.error(
                'Directory {} does not exist'.format(directory_path))
        except RuntimeError:
            logger.debug('Runtime Error caused by dictionary entry deletion' +
                         ' during program uptime. Cached file deleted from ' +
                         'dictionary despite raised exception')

        # delay next polling in accordance with interval
        time.sleep(interval)


def sync_added_files(cache, files):
    '''
    Checks for new files that are not currently being
    tracked by the cache dictionary

    Parameters:
    cache: the dictionary of files currently being tracked
    files: the list of files in the directory

    Return: an updated version of the cache dictionary with new files
    '''
    for file in files:
        if file not in cache.keys():
            cache[file] = 0
            logger.info('Added {} to file cache'.format(
                os.path.basename(file)))
    return cache


def sync_deleted_files(cache, files):
    '''
    Compares files stored in cache dictionary that are no longer
    included in the directory and deletes them.

    Parameters:
    cache: the existing cache dictionary
    files: the list of files in the directory

    Return: an updated version of the cache dictionary
    without deleted files
    '''
    for cached_file in cache.keys():
        if cached_file not in files:
            cache.pop(cached_file, None)
            logger.info('Deleted {} from file cache'.format(
                os.path.basename(cached_file)))
    return cache


def read_single_file(file_path, line_start):
    '''
    Reads a single file taking into account the lines that
    have already been read and marked in the cache dictionary

    Parameters:
    file_path: path of the file to be read
    line_start: the line of the file on which to start reading

    Return: list containing the lines that were read from file
    '''
    filename = os.path.basename(file_path)
    with open(file_path, 'r') as f:
        try:
            content = f.readlines()[line_start:]
            logger.debug('Read {} lines in {}'.format(len(content), filename))
            return content
        except IndexError:
            logger.warning('No new lines to read in file {}'.format(filename))
            return []
        except FileNotFoundError:
            logger.warning('File named {} no longer exists'. format(filename))
            return []


def check_magic_text(file_lines, magic_text, first_line_num):
    '''
    Checks for a string of text in a list of lines read from
    a file

    Parameters:
    file_lines: the lines from a file that need to be checked for specific text
    magic_text: the specific text for which to search
    first_line_num: the line number of the first line in file_lines

    Return: a list with the line numbers that contain the magic_text
    '''
    line_num = first_line_num
    matches = []
    for line in file_lines:
        if magic_text.lower() in line.lower():
            matches.append(line_num + 1)
        line_num += 1
    return matches


def main(args):
    # create parser for shell arguments
    parser = create_parser(args)
    ns = parser.parse_args()

    # logger configuration
    log_level = set_log_level(ns.loglevel)
    config_logger(log_level)

    # banner log to indicate program start
    prog_start_time = dt.now()
    logger.info(textwrap.dedent('''
    --------------------------------
        dirwatcher.py started at
        {}
        Process ID: {}
    --------------------------------'''.format(prog_start_time, os.getpid())))
    # connect signal handlers
    config_signal_handlers()

    # monitor the directory for the string of text
    watch_directory(ns.dir, ns.ext, ns.text, ns.pollint)

    # banner log to indicate program end
    prog_end_time = dt.now()
    total_uptime = prog_end_time - prog_start_time
    logger.info(textwrap.dedent('''
    --------------------------------
        dirwatcher.py ended at
        {}
        Total Uptime: {}
    --------------------------------'''.format(prog_end_time, total_uptime)))


if __name__ == '__main__':
    main(sys.argv[1:])
