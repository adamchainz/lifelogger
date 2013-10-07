#!/usr/bin/env python
# coding=utf-8
import sys

from oauth2client import client as oa2c_client

import connection
from config import config


def main(argv):
    service = connection.connect()

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
        import ipdb; ipdb.set_trace()
    except oa2c_client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")


if __name__ == '__main__':
    main(sys.argv)
