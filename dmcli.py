#!/usr/bin/python3

import os
import sys
import traceback
import argparse
import configparser
import logging
from docmaker.pipeline import build_document

def __set_cmdargs_up():
    """parses the cmd line arguments at the call"""

    psr_desc='Document maker command line control interface'
    psr_epi='The file config.ini is used to specify defaults'

    psr = argparse.ArgumentParser(description=psr_desc, epilog=psr_epi)

    psr.add_argument(
        '-d', '--debug', action='store_true',
        dest='dm_debug', help='print debug information'
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
    psr.add_argument(
        '-l', '--list', action='store_true',
        dest='dm_show', help='list builder supported modules'
    )

    return psr.parse_args()


def dmcli(s_file, args, logger):

    def read_settings():
        c = configparser.ConfigParser()
        logger.debug("looking for settings file in:\n{0}".format(
            os.path.abspath(s_file)))
        if os.path.isfile(s_file):
            c.read(s_file)
        else:
            raise Exception("unable to locate the settings file")
        return c

    logging.basicConfig(level=logging.DEBUG if args.dm_debug else logging.INFO)
    logger.debug(args)
    config = read_settings()

    if args.dm_show:
        print('list of builder supported modules')
        supported_ones = config['doc builders']['supported'].split(' ')
        for m in supported_ones:
            print("> %s" % (m))
        return

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

        file_path = build_document(
            args.dm_builder,
            logger,
            read_settings(),
            args.dm_output,
            **kwargs
        )
    else:
        raise Exception("builder module not define")

if __name__ == "__main__":

    __CONFIG_FILE = 'config.ini'

    logger = logging.getLogger(__name__)
    args = __set_cmdargs_up()
    try:
        dmcli(__CONFIG_FILE, args, logger)
        logger.info('successful builder execution')
    except:
        if args.dm_debug:
            traceback.print_exc()
        sys.exit(1)

    sys.exit(0)
