# coding=utf-8
"""
All commands that create & use the local copies of the Google Calendar data.
"""
import requests
from icalendar import Calendar

from ..config import config, ICAL_PATH

from .parser import subparsers


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
    from ..database import Event

    print "Converting iCal file into sqlite database..."

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

    print "Imported {} events.".format(
        Event.select().count()
    )

    return True

make_db.parser = subparsers.add_parser('make_db')
make_db.parser.set_defaults(func=make_db)


def shell():
    from datetime import datetime, date
    from ..database import Event, regexp

    [datetime, date, Event, regexp]

    from IPython import embed
    embed()

shell.parser = subparsers.add_parser('shell')
shell.parser.set_defaults(func=shell)


def list_command(filter_re):
    filter_re = ' '.join(filter_re)
    from ..database import Event, regexp

    events = Event.select().where(regexp(Event.summary, filter_re))

    for event in events:
        print event.display()

    return True

list_command.parser = subparsers.add_parser('list')
list_command.parser.add_argument('filter_re', nargs="+", type=unicode)
list_command.parser.set_defaults(func=list_command)
