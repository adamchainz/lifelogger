# coding=utf-8
"""
Handles connecting to Google API and authenticating.
"""
import argparse
import httplib2
import os
import sys

from apiclient import discovery as apc_discovery
from oauth2client import file as oa2c_file
from oauth2client import client as oa2c_client
from oauth2client import tools as oa2c_tools

CLIENT_SECRETS_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'client_secrets.json'
)

# Parser for command-line arguments - only used to get defaults
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[oa2c_tools.argparser]
)


FLOW = oa2c_client.flow_from_clientsecrets(
    CLIENT_SECRETS_PATH,
    scope=[
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message="Error - client_secrets.json file missing."
)


def connect():
    from config import config, DATA_PATH

    flags = parser.parse_args([])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = oa2c_file.Storage(os.path.join(DATA_PATH, 'google_auth.json'))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = oa2c_tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    try:
        service = apc_discovery.build('calendar', 'v3', http=http)
    except httplib2.ServerNotFoundError:
        sys.stderr.write("Error: server not found - are you connected to the internet?\n")
        sys.exit()

    if 'calendar_id' not in config:
        all_cals = service.calendarList().list().execute()['items']
        primary_cal = [cal for cal in all_cals
                       if 'primary' in cal and cal['primary']][0]
        config['calendar_id'] = primary_cal['id']

    if 'timezone' not in config:
        settings = service.settings().list().execute()['items']
        settings = dict([(item['id'], item['value']) for item in settings])
        config['timezone'] = settings.get('timezone', "Europe/London")

    return service
