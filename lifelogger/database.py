# coding=utf-8
import re
from datetime import datetime, time

from peewee import CharField, DateTimeField, Expression, Model, SqliteDatabase

from .config import DB_PATH
from .utils import blue, highlight_tags


# Add regex function to SqliteDatabase
OP_REGEXP = 'regexp'


def regexp(lhs, rhs):
    return Expression(lhs, 'regexp', rhs)

SqliteDatabase.register_ops({OP_REGEXP: 'REGEXP'})


# Create database reference
db = SqliteDatabase(DB_PATH)


# Define REGEXP function in sqlite database connection
conn = db.get_conn()


def regex_matches(regex, string):
    return bool(re.search(regex, string, flags=re.IGNORECASE))


conn.create_function('REGEXP', 2, regex_matches)


# Models
class Event(Model):
    summary = CharField()
    start = DateTimeField()
    end = DateTimeField()

    class Meta:
        database = db
        indexes = (
            (('summary'), False),
            (('start'), False),
            (('end'), False),
        )
        order_by = ('start',)

    @classmethod
    def create_from_ical_event(cls, ical_event):
        return cls.create(
            summary=ical_event.get('summary'),
            start=normalized(ical_event.get('dtstart').dt),
            end=normalized(ical_event.get('dtend').dt),
        )

    def __unicode__(self):
        return u"{}    {}    {}".format(
            self.start,
            self.end,
            self.summary,
        )

    def display(self):
        # Pretty tabular formatting.
        start = self.start.strftime('%Y %b %d %H:%M')
        end = self.end.strftime('%b %d %H:%M')

        return "{}\t{}\t{}".format(
            blue(start),
            blue(end),
            highlight_tags(self.summary)
        )

    @property
    def duration_seconds(self):
        return (self.end - self.start).total_seconds()

    @property
    def duration_minutes(self):
        return self.duration_seconds / 60.0

    @property
    def kg(self):
        return self.number_property('kg', '([0-9.]+)kg\\b')

    @property
    def mg(self):
        return self.number_property('mg', '([0-9.]+)mg\\b')

    def number_property(self, name, regex):
        try:
            return float(
                re.search(regex, self.summary).group(1)
            )
        except ValueError:
            raise ValueError("Event {} has no variable {}".format(self, name))


def normalized(dt):
    # Fix the broken API for ical events - dt may be a date or datetime, so
    # make sure it is a datetime
    if not isinstance(dt, datetime):
        dt = datetime.combine(dt, time(0))

    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt
