# coding=utf-8
import re
import sys

from termcolor import colored


if sys.stdout.isatty():
    blue = lambda x: colored(x, 'blue')
    pink = lambda x: colored(x, 'magenta')
else:
    blue = lambda x: x
    pink = lambda x: x


def highlight_tags(string):
    highlight = lambda match: pink(match.group(0))

    return re.sub(
        r'\#\w+\b',
        highlight,
        string,
        flags=re.MULTILINE
    )
