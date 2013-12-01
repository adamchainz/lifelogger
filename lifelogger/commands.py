# coding=utf-8
import argparse
import re
import sys
from datetime import datetime, timedelta

import dateutil.parser
import requests
from icalendar import Calendar

from .connection import connect
from .config import config, ICAL_PATH


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


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


def now(summary, offset=0, duration=None):
    if duration is None:
        duration = 0

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
now.parser.add_argument('offset', type=int, default=0, nargs='?')
now.parser.add_argument('-d', '--duration', type=int)
now.parser.add_argument('summary')
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


def download(reset=None):
    if reset:
        config.pop('ical_url', None)

    try:
        ical_url = config['ical_url']
    except KeyError:
        print "To download the iCal file for analysis, you must give me the public URL for it."
        print "Please go to the Google Calendar web interface, 'Calendar Settings', and then copy the link address from the ICAL button under 'Calendar Address'"
        ical_url = raw_input("Paste --> ")
        config['ical_url'] = ical_url

    print "Downloading private iCal file..."
    req = requests.get(ical_url, stream=True)

    if req.status_code != 200:
        print "Could not fetch iCal url - has it expired? To change, run download --reset"
        print ical_url
        return False

    with open(ICAL_PATH, 'wb') as f:
        for chunk in req.iter_content():
            f.write(chunk)

    print "Download successful!"

    make_db()

    return True

download.parser = subparsers.add_parser('download')
download.parser.add_argument('-r', '--reset', const=True, default=False, nargs='?')
download.parser.set_defaults(func=download)


def make_db():
    from .analyzer import Event

    print "Converting iCal file into sqlite database for faster querying..."

    with open(ICAL_PATH, 'rb') as f:
        ical_data = f.read()

    cal = Calendar.from_ical(ical_data)

    try:
        Event.drop_table()
    except:
        pass
    try:
        Event.create_table()
    except:
        pass

    for event in cal.walk("VEVENT"):
        Event.create_from_ical_event(event)

    print "Imported {} events into sqlite database.".format(
        Event.select().count()
    )

    return True

make_db.parser = subparsers.add_parser('make_db')
make_db.parser.set_defaults(func=make_db)


def shell():
    from datetime import datetime, date
    from .analyzer import Event, regexp

    [datetime, date, Event, regexp]

    from IPython import embed
    embed()

shell.parser = subparsers.add_parser('shell')
shell.parser.set_defaults(func=shell)


def list_command(filter_re):
    filter_re = ' '.join(filter_re)
    from .analyzer import Event, regexp

    events = Event.select().where(regexp(Event.summary, filter_re))

    for event in events:
        print event

    return True

list_command.parser = subparsers.add_parser('list')
list_command.parser.add_argument('filter_re', nargs="+", type=unicode)
list_command.parser.set_defaults(func=list_command)
