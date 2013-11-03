# coding=utf-8
import argparse
import re
import sys


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()


def quickadd(text):
    import connection
    from config import config

    service = connection.connect()

    # Double up single-time events to be 0-length
    match = re.match(r'^\d\d:\d\d\b', text)
    if match:
        text = match.group(0) + '-' + text

    # Make request
    print "Quick add >>", text

    result = service.events().quickAdd(
        calendarId=config['calendar_id'],
        text=text
    ).execute()

    if result['status'] == 'confirmed':
        print "Added! Link: ", result['htmlLink']
        return True
    else:
        sys.stdout.write("Failed :( - status %s\n" % result['status'])
        return False

parser_quickadd = subparsers.add_parser('quickadd')
parser_quickadd.add_argument('text')
parser_quickadd.set_defaults(func=quickadd)
