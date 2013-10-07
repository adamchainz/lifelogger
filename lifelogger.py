#!/usr/bin/env python
# coding=utf-8
import sys

from oauth2client import client as oa2c_client

import connection


def main(argv):
    service = connection.connect()

    try:
        import ipdb; ipdb.set_trace()
    except oa2c_client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")


if __name__ == '__main__':
    main(sys.argv)
