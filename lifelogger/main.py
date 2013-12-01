#!/usr/bin/env python
# coding=utf-8
import sys

from oauth2client import client as oa2c_client

from .commands import parser


def main(argv):
    if len(sys.argv) <= 1:
        parser.print_help()
        return True

    kwargs = dict(parser.parse_args(sys.argv[1:])._get_kwargs())
    func = kwargs.pop('func')

    try:
        return func(**kwargs)
    except oa2c_client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")


if __name__ == '__main__':
    success = main(sys.argv)
    sys.exit(0 if success else 1)
