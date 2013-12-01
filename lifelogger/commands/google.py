# coding=utf-8
"""
All commands that call the Google API service.
"""
import re
import sys
from datetime import datetime, timedelta

import dateutil.parser

from ..connection import connect
from ..config import config

from .parser import subparsers


def quickadd(summary):
    service = connect()

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

quickadd.parser = subparsers.add_parser('quickadd')
quickadd.parser.add_argument('summary')
quickadd.parser.set_defaults(func=quickadd)


def now(summary, offset=None, duration=None):
    if offset is None:
        offset = 0

    if duration is None:
        duration = 0

    summary = ' '.join(summary)

    service = connect()

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

now.parser = subparsers.add_parser('now')
now.parser.add_argument('-o', '--offset', type=int)
now.parser.add_argument('-d', '--duration', type=int)
now.parser.add_argument('summary', nargs="+", type=unicode)
now.parser.set_defaults(func=now)


def for_command(duration, summary):
    service = connect()

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

for_command.parser = subparsers.add_parser('for')
for_command.parser.add_argument('duration', type=int)
for_command.parser.add_argument('summary')
for_command.parser.set_defaults(func=for_command)


def add(summary, when=None, duration=0):
    if when is None:
        when = datetime.now()
    else:
        when = dateutil.parser.parse(when)

    service = connect()

    times = [
        when,
        when + timedelta(minutes=duration)
    ]
    times.sort()
    start, end = times

    print "Adding %i-minute event at %s >> %s" % (abs(duration), when, summary)

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


add.parser = subparsers.add_parser('add')
add.parser.add_argument('-w', '--when', default=None)
add.parser.add_argument('summary')
add.parser.set_defaults(func=add)

