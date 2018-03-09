# coding=utf-8
from __future__ import absolute_import
import re
import sys
from datetime import datetime

from termcolor import colored


if sys.stdout.isatty():
    def blue(string):
        return colored(string, 'blue')

    def pink(string):
        return colored(string, 'magenta')
else:
    def blue(string):
        return string

    def pink(string):
        return string


def highlight_tags(string):
    def highlight(match):
        return pink(match.group(0))

    return re.sub(
        r'\#\w+\b',
        highlight,
        string,
        flags=re.MULTILINE
    )


def nice_format(var):
    if isinstance(var, datetime):
        return var.isoformat()
    else:
        return str(var)
