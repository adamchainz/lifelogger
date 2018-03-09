# coding=utf-8
"""
All commands that create & use the local copies of the Google Calendar data.
"""
from __future__ import absolute_import, print_function

import requests

from icalendar import Calendar

from ..config import config, ICAL_PATH
from ..utils import nice_format

from .parser import subparsers
import six
from six.moves import input


def download(reset=None):
    if reset:
        config.pop('ical_url', None)

    try:
        ical_url = config['ical_url']
    except KeyError:
        print("To download the iCal file for analysis, you must give me the "
              "public URL for it.")
        print("Please go to the Google Calendar web interface "
              ", 'Calendar Settings', and then copy the link address from "
              "the ICAL button under 'Calendar Address'")
        ical_url = input("Paste --> ")
        config['ical_url'] = ical_url

    print("Downloading private iCal file...")
    req = requests.get(ical_url, stream=True)

    if req.status_code != 200:
        print("Could not fetch iCal url - has it expired? ")
        print("To change, run download --reset")
        print(ical_url)
        return False

    with open(ICAL_PATH, 'wb') as f:
        for chunk in req.iter_content():
            f.write(chunk)

    print("Download successful!")

    make_db()

    return True


download.parser = subparsers.add_parser(
    'download',
    description="Downloads the iCal that contains the whole of your Google "
                "Calendar, and then parses it into the local database"
)
download.parser.add_argument(
    '-r',
    '--reset',
    const=True,
    default=False,
    nargs='?',
    help="Pass this in to force re-pasting in the iCal url, if e.g. the url "
         " stored in lifelogger is no longer valid."
)
download.parser.set_defaults(func=download)


def make_db():
    from ..database import Event, db

    print("Converting iCal file into sqlite database...")

    with open(ICAL_PATH, 'rb') as f:
        ical_data = f.read()

    cal = Calendar.from_ical(ical_data)

    try:
        Event.drop_table()
    except Exception:
        pass

    try:
        Event.create_table()
    except Exception:
        pass

    with db.atomic():
        for event in cal.walk("VEVENT"):
            Event.create_from_ical_event(event)

    print("Imported {} events.".format(
        Event.select().count()
    ))

    return True


make_db.parser = subparsers.add_parser(
    'make_db',
    description="Parses the downloaded iCal file into the local sqlite "
                "database. Normally done when the download command is run, "
                "but may need re-running on changes to lifelogger."
)
make_db.parser.set_defaults(func=make_db)


def shell():
    from datetime import datetime, date  # noqa
    from ..database import Event, regexp  # noqa

    from IPython import embed
    embed()


shell.parser = subparsers.add_parser(
    'shell',
    description="Loads the local database and an IPython shell so you can "
                "manually search around the events using the 'peewee' ORM."
)
shell.parser.set_defaults(func=shell)


def sql(statement, separator):
    from ..database import conn
    statement = ' '.join(statement)

    cursor = conn.cursor()
    cursor.execute(statement)

    separator = {
        'comma': ',',
        'semicolon': ';',
        'tab': '\t',
    }[separator]

    # Header
    print(separator.join([d[0] for d in cursor.description]))

    # Data
    for row in cursor.fetchall():
        print(separator.join([str(v) for v in row]))


sql.parser = subparsers.add_parser(
    'sql',
    description="Execute a SQL statement direct on the db and output results "
                "as csv."
)
sql.parser.add_argument(
    'statement',
    nargs="+",
    type=six.text_type,
    help="The SQL statement."
)
sql.parser.add_argument(
    '-s',
    '--separator',
    nargs="?",
    type=six.text_type,
    default="comma",
    choices=['comma', 'semicolon', 'tab'],
    help="Separator for the output - default comma."
)
sql.parser.set_defaults(func=sql)


def list_command(filter_re):
    filter_re = ' '.join(filter_re)
    from ..database import Event, regexp

    events = Event.select().where(regexp(Event.summary, filter_re))

    for event in events:
        print(event.display())

    return True


list_command.parser = subparsers.add_parser(
    'list',
    description="Lists the events that match a given regex."
)
list_command.parser.add_argument(
    'filter_re',
    nargs="+",
    type=six.text_type,
    help="The regex to filter events by."
)
list_command.parser.set_defaults(func=list_command)


def csv(filter_re, separator, varnames):
    filter_re = ' '.join(filter_re)

    varnames = varnames.split(',')

    separator = {
        'comma': ',',
        'semicolon': ';',
        'tab': '\t',
    }[separator]

    from ..database import Event, regexp

    events = Event.select().where(regexp(Event.summary, filter_re))

    # Header
    print(separator.join(varnames))

    # Data
    for event in events:
        print(separator.join([
            nice_format(event.get_var(varname)) for varname in varnames
        ]))


csv.parser = subparsers.add_parser(
    'csv',
    description="Used to output properties of events that a given filter as "
                "CSV data."
)
csv.parser.add_argument(
    '-s',
    '--separator',
    nargs="?",
    type=six.text_type,
    default="comma",
    choices=['comma', 'semicolon', 'tab'],
    help="Separator for the output - default comma."
)
csv.parser.add_argument(
    '-v',
    '--varnames',
    nargs="?",
    type=six.text_type,
    default="start,end,summary",
    help="A comma-separated list of the Event variables to output (options: "
         "start, end, summary, duration_seconds, duration_minutes, "
         "duration_hours, units, percentage, kg, mg). "
         "Defaults to 'start,end,summary'."
)
csv.parser.add_argument(
    'filter_re',
    nargs="+",
    type=six.text_type,
    help="The regex to filter events by."
)
csv.parser.set_defaults(func=csv)
