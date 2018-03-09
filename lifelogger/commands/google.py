# coding=utf-8
"""
All commands that call the Google API service.
"""
from __future__ import absolute_import
from __future__ import print_function
import re
import sys
from datetime import datetime, timedelta

import dateutil.parser

from ..connection import connect
from ..config import config

from .parser import subparsers
import six


def quickadd(summary):
    summary = ' '.join(summary)

    service = connect()

    # Double up single-time events to be 0-length
    match = re.match(r'^\d\d:\d\d ', summary)
    if match:
        summary = match.group(0)[:-1] + '-' + summary

    # Make request
    print("Quick add >>", summary)

    result = service.events().quickAdd(
        calendarId=config['calendar_id'],
        text=summary
    ).execute()

    if result['status'] == 'confirmed':
        print("Added! Link: ", result['htmlLink'])
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

quickadd.parser = subparsers.add_parser(
    'quickadd',
    description="Use 'quick-add' to add an event to your calendar - works the "
                "same as the Google Calendar web interface function, with "
                "some extensions. To add a 0-minute event at a particular "
                "time today, run with the time in 24-hour format at the "
                "start, e.g. '10:00 Coffee'."
)
quickadd.parser.add_argument(
    'summary',
    help="The summary for the event.",
    nargs='*'
)
quickadd.parser.set_defaults(func=quickadd)


def now(summary, duration):
    try:
        offset = int(summary[0])
        summary = summary[1:]
    except ValueError:
        offset = 0

    summary = ' '.join(summary)

    service = connect()

    start = datetime.now() + timedelta(minutes=offset)
    end = start + timedelta(minutes=duration)

    print("Adding %i-minute event >> %s" % (duration, summary))

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
        print("Added! Link: ", result['htmlLink'])
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

now.parser = subparsers.add_parser(
    'now',
    description="Adds an event 'right now'.")
now.parser.add_argument(
    '-d',
    '--duration',
    type=int,
    default=0,
    help="The duration of the event (default 0)"
)
now.parser.add_argument(
    'summary',
    nargs="+",
    type=six.text_type,
    help="The summary for the event."
)
now.parser.set_defaults(func=now)


def for_command(duration, summary):
    summary = ' '.join(summary)

    service = connect()

    times = [
        datetime.now(),
        datetime.now() + timedelta(minutes=duration)
    ]
    times.sort()
    start, end = times

    print("Adding %i-minute event >> %s" % (abs(duration), summary))

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
        print("Added! Link: ", result['htmlLink'])
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

for_command.parser = subparsers.add_parser(
    'for',
    description="Adds an event that lasts *for* the specified number of "
                "minutes, relative to now."
)
for_command.parser.add_argument(
    'duration',
    type=int,
    help="The duration of the event. Give a negative number, and the event "
         "will be set to have started 'duration' minutes ago, and end now; "
         "otherwise it starts now and ends in 'duration' minutes time."
)
for_command.parser.add_argument(
    'summary',
    help="The summary for the event.",
    nargs='*'
)
for_command.parser.set_defaults(func=for_command)


def add(summary, start=None, end=None, duration=None):
    summary = ' '.join(summary)

    if start is None:
        start = datetime.now()
    else:
        start = dateutil.parser.parse(start)

    if end is not None:
        end = dateutil.parser.parse(end)

    if duration is None:
        duration = 0

    if end is None:
        end = start + timedelta(minutes=duration)

    service = connect()

    times = [start, end]
    times.sort()
    start, end = times

    duration = (end - start).total_seconds() / 60

    print("Adding {length}-minute event at {start} >> {summary}".format(
        length=abs(duration),
        start=start,
        summary=summary
    ))

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
        print("Added! Link: ", result['htmlLink'])
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False


add.parser = subparsers.add_parser(
    'add',
    description="Generic event adding command, with all the bells and "
                "whistles."
)
add.parser.add_argument(
    '-s',
    '--start',
    default=None,
    help="The start time for the event - default is now."
)
add.parser.add_argument(
    '-e',
    '--end',
    default=None,
    help="The end time for the event - default is to make a 0-minute event."
)
add.parser.add_argument(
    '-d',
    '--duration',
    default=None,
    type=int,
    help="The duration, in minutes, for the event. If both end and duration "
         "are set, duration overrides. Can be negative."
)
add.parser.add_argument(
    'summary',
    help="The summary for the event.",
    nargs='*'
)
add.parser.set_defaults(func=add)
