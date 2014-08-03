#!/usr/bin/env python
"""
Take notes from Notes.app and turn them into lifelogger events, putting those
that were converted into an 'Archive' folder on the way. It is your
responsibility to clear the 'Archive' folder before re-running, otherwise you
will get duplicate events. You'll also probably want to update the import
functions as you'll be using different syntax to me.

Needs two extra dependencies from lifelogger - sh and lxml. Runs the
accompanying applescript to export to json before loading here.
"""
import codecs
import json
import os
import re
import shutil
import sys
import tempfile

import dateutil.parser
try:
    import sh
    from lxml.html import document_fromstring
except ImportError:
    print "Need 'sh' and 'lxml'. `pip install sh lxml` to fix."
    sys.exit()

NOTES_TO_JSON_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'notes-to-json.applescript'
)

notes_to_json = sh.Command(NOTES_TO_JSON_PATH)
lifelogger = sh.lifelogger
osascript = sh.osascript


def main():
    print "Exporting from Notes.app"
    notes = dump_and_load_notes()

    print "Running import functions"
    import_weights_to_lifelogger(notes)

    import_cms_to_lifelogger(notes)


def dump_and_load_notes():
    temp_dir = tempfile.mkdtemp(prefix='notes_to_calendar')
    notes_path = os.path.join(temp_dir, 'notes.json')

    notes_to_json(notes_path)

    notes = load_notes(notes_path)

    shutil.rmtree(temp_dir)
    return notes


def load_notes(path):
    with codecs.open(path, 'r') as f:
        notedata = f.read().decode('utf-8', 'replace')

    notedata = notedata.replace('\t', ' ')

    notes = json.loads(notedata)

    for note in notes:
        body = note['body'].replace('<br>', '\n ')
        body = document_fromstring(body).text_content()
        body = body.strip()
        note['body'] = body

        note['when'] = dateutil.parser.parse(note['creationDate'])

    return notes


weights_re = re.compile("""
    ^
    (Chest\ press|
     Pec\ fly|
     Seated\ row|
     Pull\ down|
     Seated\ curl|
     Leg\ extension|
     Shoulder\ press|
     Leg\ Press[2]?)
    \s+
    (\d+)kg
    \s+
    (\d+)s  # time
    \s*
    $
""", re.VERBOSE | re.IGNORECASE)


def import_weights_to_lifelogger(notes):
    for note in notes:
        body = note['body']
        match = weights_re.match(body)
        if match:

            exercise, weight, seconds = match.groups()
            event = "{} {}kg seconds={} #exercise".format(
                exercise, weight, seconds)

            print note
            print note['when'], event
            import ipdb; ipdb.set_trace()

            print lifelogger('add', '--start', note['when'].isoformat(), event)
            archive_note(note['id'])


def import_cms_to_lifelogger(notes):
    event = 'Clenil Modulite 200mcg #drugs'
    for note in notes:
        if note['body'].lower() == 'cm':
            print note
            import ipdb; ipdb.set_trace()
            print lifelogger('add', '--start', note['when'].isoformat(), event)
            archive_note(note['id'])


def archive_note(note_id):
    osascript(e="""
    tell application "Notes"
        set m to (every note whose id is "{}")
        move (item 1 of m) to folder "Archive"
    end tell""".format(note_id).strip())


if __name__ == '__main__':
    main()
