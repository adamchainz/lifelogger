#!/usr/bin/env python
# coding=utf-8
import httplib2
import sys

from oauth2client import client as oa2c_client

import connection
from config import config
from commands import parser


def main(argv):
    try:
        service = connection.connect()
    except httplib2.ServerNotFoundError:
        sys.stderr.write("Server not found\n")
        return False

    if 'calendar_id' not in config:
        all_cals = service.calendarList().list().execute()['items']
        primary_cal = [cal for cal in all_cals
                       if 'primary' in cal and cal['primary']][0]
        config['calendar_id'] = primary_cal['id']
        config.save()

    if 'timezone' not in config:
        settings = service.settings().list().execute()['items']
        settings = dict([(item['id'], item['value']) for item in settings])
        config['timezone'] = settings.get('timezone', "Europe/London")
        config.save()

    try:
        if len(sys.argv) <= 1:
            parser.print_help()
            return True

        args = parser.parse_args(sys.argv[1:])
        return args.func(service, config, args)
    except oa2c_client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")


if __name__ == '__main__':
    success = main(sys.argv)
    sys.exit(0 if success else 1)
