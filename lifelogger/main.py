#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import
from __future__ import print_function
import sys

from oauth2client import client as oa2c_client

from .commands import parser


def main():
    if len(sys.argv) <= 1:
        parser.print_help()
        return True

    kwargs = dict(parser.parse_args(sys.argv[1:])._get_kwargs())
    func = kwargs.pop('func')

    try:
        successful = func(**kwargs)
        sys.exit(0 if successful else 1)
    except oa2c_client.AccessTokenRefreshError:
        print("The credentials have been revoked or expired, please re-run" \
              "the application to re-authorize")
        sys.exit(1)


if __name__ == '__main__':
    main()
