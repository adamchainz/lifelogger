# coding=utf-8
from __future__ import absolute_import

import argparse

description = """
lifelogger: Track your life like a pro on Google Calendar via your terminal.

An all-in-one solution for adding events quickly, downloading them all into a
local SQLite database, and analyzing/exporting them.

To discover more about a command, run it with '--help', e.g.
'lifelogger download --help'.

Try starting with the 'add', 'download', and 'list' commands.
"""

# The main parser
parser = argparse.ArgumentParser(
    prog="lifelogger",
    description=description,
    epilog="Enjoy! Adam"
)

subparsers = parser.add_subparsers()
