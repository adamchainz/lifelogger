# coding=utf-8
"""
Handles connecting to Google API and authenticating.
"""
import argparse
import httplib2
import os

from apiclient import discovery as apc_discovery
from oauth2client import file as oa2c_file
from oauth2client import client as oa2c_client
from oauth2client import tools as oa2c_tools


CLIENT_SECRETS_PATH = os.path.join(os.path.dirname(__file__), 'client_secrets.json')


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
    message=oa2c_tools.message_if_missing(CLIENT_SECRETS_PATH)
)


def connect():
    flags = parser.parse_args([])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = oa2c_file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = oa2c_tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = apc_discovery.build('calendar', 'v3', http=http)

    return service
