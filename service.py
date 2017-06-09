#!/usr/bin/python3

import traceback
import argparse
import logging
import sys

def listener_configurer(log_path, debug):

    # if no name is specified, return a logger
    # which is the root logger of the hierarchy.
    root = logging.getLogger()

    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler(log_path, when="d",
        interval=1, backupCount=7)
    fh.setLevel(logging.DEBUG if debug else logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # create formatters and add them to the handlers
    fhFormatter = logging.Formatter(
        '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    chFormatter = logging.Formatter(
        '%(processName)-10s %(name)s %(levelname)-8s - %(filename)s - Line: %(lineno)d - %(message)s')
    fh.setFormatter(fhFormatter)
    ch.setFormatter(chFormatter)

    # add the handlers to root
    root.addHandler(ch)
    root.addHandler(fh)

def listener_process(queue, configurer, log_path, debug=False):
    configurer(log_path, debug)
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":

    def parse_cmdline():
        """parses the command line arguments at the call."""

        psr_desc="cfdi engine service interface"
        psr_epi="select a config profile to specify defaults"

        psr = argparse.ArgumentParser(
                    description=psr_desc, epilog=psr_epi)

        psr.add_argument('-d', action='store_true', dest='debug',
                                help='print debug information')

        psr.add_argument('-c', '--config', action='store',
                               dest='config',
                               help='load an specific config profile')

        psr.add_argument('-p', '--port', action='store',
                               dest='port',
                               help='launches service on specific port')

        return psr.parse_args()

    args = parse_cmdline()

    RESOURCES_DIR = '{}/resources'.format(expanduser("~"))
    PROFILES_DIR = '{}/profiles'.format(RESOURCES_DIR)
    LOGS_DIR = '{}/logs'.format(RESOURCES_DIR)
    LOG_NAME = 'blcore'
    DEFAULT_PORT = 10080
    DEFAULT_PROFILE = 'default.json'

    log_path = '{}/{}.log'.format(LOGS_DIR, LOG_NAME)
    profile_path = '{}/{}'.format(PROFILES_DIR,
        args.config if args.config else DEFAULT_PROFILE))

    queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=listener_process,
        args=(queue, listener_configurer, log_path, args.debug))
    listener.start()


