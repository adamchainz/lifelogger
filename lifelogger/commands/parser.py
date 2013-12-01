# coding=utf-8
import argparse

# The main parser
parser = argparse.ArgumentParser(
    prog="lifelogger",
    description="""lifelogger: Track your life like a pro on Google Calendar via your terminal.

    An all-in-one solution for adding events quickly, downloading them all into a database, and analyzing/exporting them.

    To discover more about a command, run it with '--help', e.g. 'lifelogger download --help'. Try starting with the add', 'download', and 'list' commands.
    """,
    epilog="Enjoy! Adam"
)

subparsers = parser.add_subparsers()
