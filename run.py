#!/usr/bin/python3

from misc.factory import Factory
from bbgum.server import BbGumServer, BbGumServerError
from custom.profile import ProfileReader
from misc.tricks import dict_params
from os.path import expanduser
from logging.handlers import TimedRotatingFileHandler
import os
import inspect
import traceback
import argparse
import logging
import sys

sys.path.append(
    os.path.abspath(os.path.join(
        os.path.dirname(__file__), "controllers")))

def setup_log(logs_dir, debug=False):
    '''Setup the overall of handlers needed '''

    LOGGER_NAME = 'blcore'
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler('{}/{}.log'.format(logs_dir, LOGGER_NAME),
                                       when="d",
                                       interval=1,
                                       backupCount=7)
    fh.setLevel(logging.DEBUG if debug else logging.INFO)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    fhFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    chFormatter = logging.Formatter('%(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s')
    fh.setFormatter(fhFormatter)
    ch.setFormatter(chFormatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info("-----------------------------------")
    logger.info("Log system successfully initialized")
    logger.info("-----------------------------------")

    return logger

def go_service(args):

    def read_settings(s_file):
        logger.debug("looking for config profile file in:\n{0}".format(
            os.path.abspath(s_file)))
        if os.path.isfile(s_file):
            reader = ProfileReader(logger)
            return reader(s_file)
        raise Exception("unable to locate the config profile file")

    def getup_factory(logger, variants):
        devents = dict_params(
            ProfileReader.get_content(
            variants, ProfileReader.PNODE_MANY),
            'archetype', 'event_mod')
        fact = Factory()
        for archetype, event_mod in devents.items():
            try:
                m = __import__(event_mod)

                if not hasattr(m, "impt_class"):
                    msg = "module {0} has no impt_class attribute".format(event_mod)
                    raise RuntimeError(msg)
                cname = getattr(m, "impt_class")

                if not hasattr(m, cname):
                    msg = "module {0} has no {1} class implemented".format(event_mod, cname)
                    raise RuntimeError(msg)
                ic = getattr(m, cname)
                fact.subscribe(int(archetype, 0), ic)
            except (ImportError, RuntimeError) as e:
                logger.fatal("{0} support library failure".format(event_mod))
                raise e
        return fact

    RESOURCES_DIR = '{}/resources'.format(expanduser("~"))
    PROFILES_DIR = '{}/profiles'.format(RESOURCES_DIR)
    LOGS_DIR = '{}/logs'.format(RESOURCES_DIR)
    DEFAULT_PORT = 10080
    DEFAULT_PROFILE = 'default.json'

    logger = setup_log(LOGS_DIR, args.debug)

    logger.debug(args)

    port = int(args.port) if args.port else DEFAULT_PORT

    pt = read_settings(
        '{}/{}'.format(
            PROFILES_DIR,
            args.config if args.config else DEFAULT_PROFILE))

    try:
        service = BbGumServer(logger, port)
        service.start(getup_factory(logger, pt.bbgum.controllers), forking = not args.nmp)
    except (BbGumServerError) as e:
        logger.error(e)
        raise


if __name__ == "__main__":

    def setup_parser():
        """parses the command line arguments at the call."""

        psr_desc="cfdi engine service interface"
        psr_epi="select a config profile to specify defaults"

        psr = argparse.ArgumentParser(
                    description=psr_desc, epilog=psr_epi)

        psr.add_argument('-nmp', action='store_true', dest='nmp',
                                help='unique process approach (useful in development)')

        psr.add_argument('-d', action='store_true', dest='debug',
                                help='print debug information')

        psr.add_argument('-c', '--config', action='store',
                               dest='config',
                               help='load an specific config profile')

        psr.add_argument('-p', '--port', action='store',
                               dest='port',
                               help='launches service on specific port')

        return psr.parse_args()

    args = setup_parser()
    try:
        go_service(args)
    except:
        if args.debug:
            traceback.print_exc()
        sys.exit(1)
    # assuming everything went right, exit gracefully
    sys.exit(0)
