#!/usr/bin/python3

import os
import sys
import traceback
import argparse
import logging
from os.path import expanduser
from docmaker.pipeline import DocPipeLine
from custom.profile import ProfileReader

def __set_cmdargs_up():
    """parses the cmd line arguments at the call"""

    psr_desc='Document maker command line control interface'
    psr_epi='The config profile is used to specify defaults'

    psr = argparse.ArgumentParser(description=psr_desc, epilog=psr_epi)

    psr.add_argument(
        '-d', '--debug', action='store_true',
        dest='dm_debug', help='print debug information'
    )
    psr.add_argument(
        '-c', '--config', action='store',
        dest='config', help='load an specific config profile'
    )
    psr.add_argument(
        '-b', '--builder',
        dest='dm_builder', help='specify the builder to use'
    )
    psr.add_argument(
        '-i', '--input',
        dest='dm_input', help='specify the input variables with \'var=val;var2=val2;var2=valN\'..'
    )
    psr.add_argument(
        '-o', '--output',
        dest='dm_output', help='specify the output file'
    )

    return psr.parse_args()


def dmcli(s_file, args, logger):

    def read_settings():
        logger.debug("looking for config profile file in:\n{0}".format(
            os.path.abspath(s_file)))
        if os.path.isfile(s_file):
            reader = ProfileReader(logger)
            return reader(s_file)
        raise Exception("unable to locate the config profile file")

    logging.basicConfig(level=logging.DEBUG if args.dm_debug else logging.INFO)
    logger.debug(args)
    pt = read_settings()

    if not args.dm_output:
        raise Exception("not defined output file")

    if args.dm_builder:
        if not args.dm_input:
            raise Exception("not defined input variables")

        kwargs = {}
        try:
            if args.dm_input.find(';') == -1:
                raise Exception("input variables bad conformed")
            else:
                for opt in args.dm_input.split(';'):
                    if opt.find('=') == -1:
                        continue
                    (k , v) = opt.split('=')
                    kwargs[k] = v
        except ValueError:
            raise Exception("input variables bad conformed")

        try:
            dpl = DocPipeLine(logger,
                rdirs_conf = pt.res.dirs,
                pgsql_conf = pt.dbms.pgsql_conn)
            dpl.run(args.dm_builder, args.dm_output, **kwargs)
        except:
            raise Exception("problems in document pipeline")
    else:
        raise Exception("builder module not define")

if __name__ == "__main__":

    RESOURCES_DIR = '{}/resources'.format(expanduser("~"))
    PROFILES_DIR = '{}/profiles'.format(RESOURCES_DIR)
    DEFAULT_PROFILE = 'default.json'

    logger = logging.getLogger(__name__)
    args = __set_cmdargs_up()

    prof = '{}/{}'.format(PROFILES_DIR,
        args.config if args.config else DEFAULT_PROFILE)

    try:
        dmcli(prof, args, logger)
        logger.info('successful builder execution')
    except:
        if args.dm_debug:
            traceback.print_exc()
        sys.exit(1)

    sys.exit(0)
