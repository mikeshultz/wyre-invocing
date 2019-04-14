#!/bin/env python
import sys
import argparse
from .crypt import create_keyfile
from .log import get_logger

log = get_logger(__name__)


def main(argv=None):
    """ CLI interaction """
    parser = argparse.ArgumentParser(description='Utility Commands')
    parser.add_argument('command', metavar='COMMAND', type=str, nargs=1,
                        help='The command to run')

    args = parser.parse_args(argv)

    if not args.command:
        log.error('A command must be provided')
        sys.exit(1)

    log.debug('Command: '.format(args.command[0]))

    if args.command[0] == 'createkey':
        create_keyfile()


if __name__ == '__main__':
    main(sys.argv[1:])
