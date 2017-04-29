from api.service import CfdiEngine, CfdiEngineError

import os
import inspect
import traceback
import argparse
import logging
import sys

def setup_log(debug=False):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(__name__ + '.log')
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

    RESOURCES_DIR = 'resources'
    PROFILES_DIR = '{0}/profiles'.format(RESOURCES_DIR)
    DEFAULT_PORT = 10080
    DEFAULT_PROFILE = 'default.json'

    logger = setup_log(args.debug)

    logger.debug(args)

    port = int(args.port) if args.port else DEFAULT_PORT
    prof = '{}/{}'.format(
        PROFILES_DIR,
        args.config if args.config else DEFAULT_PROFILE)

    try:
        service = CfdiEngine(logger, prof, port)
        service.start()
    except (CfdiEngineError) as e:
        logger.error(e)
        raise


if __name__ == "__main__":

    def setup_parser():
        """parses the command line arguments at the call."""

        psr_desc="Cfdi engine service interface"
        psr_epi="Select a config profile to specify defaults"

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

    try:
        args = setup_parser()
        go_service(args)
    except:
        if args.debug:
            traceback.print_exc()
        sys.exit(1)
    # assuming everything went right, exit gracefully
    sys.exit(0)
