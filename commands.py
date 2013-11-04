# coding=utf-8
import argparse
import re
import sys
from datetime import datetime, timedelta

import connection


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


def quickadd(summary):
    from config import config

    service = connection.connect()

    # Double up single-time events to be 0-length
    match = re.match(r'^\d\d:\d\d ', summary)
    if match:
        summary = match.group(0)[:-1] + '-' + summary

    # Make request
    print "Quick add >>", summary

    result = service.events().quickAdd(
        calendarId=config['calendar_id'],
        summary=summary
    ).execute()

    if result['status'] == 'confirmed':
        print "Added! Link: ", result['htmlLink']
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

parser_quickadd = subparsers.add_parser('quickadd')
parser_quickadd.add_argument('summary')
parser_quickadd.set_defaults(func=quickadd)


def now(summary, offset=0, duration=0):
    from config import config

    service = connection.connect()

    start = datetime.now() + timedelta(minutes=offset)
    end = start + timedelta(minutes=duration)

    print "Adding %i-minute event >> %s" % (duration, summary)

    result = service.events().insert(
        calendarId=config['calendar_id'],
        body={
            'summary': summary,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': config['timezone']
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': config['timezone']
            }
        }
    ).execute()

    if result['status'] == 'confirmed':
        print "Added! Link: ", result['htmlLink']
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

parser_now = subparsers.add_parser('now')
parser_now.add_argument('offset', type=int, default=0, nargs='?')
parser_now.add_argument('-d', '--duration', type=int)
parser_now.add_argument('summary')
parser_now.set_defaults(func=now)


def for_command(duration, summary):
    from config import config

    service = connection.connect()

    times = [
        datetime.now(),
        datetime.now() + timedelta(minutes=duration)
    ]
    times.sort()
    start, end = times

    print "Adding %i-minute event >> %s" % (abs(duration), summary)

    result = service.events().insert(
        calendarId=config['calendar_id'],
        body={
            'summary': summary,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': config['timezone']
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': config['timezone']
            }
        }
    ).execute()

    if result['status'] == 'confirmed':
        print "Added! Link: ", result['htmlLink']
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

parser_for = subparsers.add_parser('for')
parser_for.add_argument('duration', type=int)
parser_for.add_argument('summary')
parser_for.set_defaults(func=for_command)
