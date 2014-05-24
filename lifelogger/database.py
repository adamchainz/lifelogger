# coding=utf-8
import re
from datetime import datetime, time

from peewee import CharField, DateTimeField, Expression, Model, SqliteDatabase

from .config import DB_PATH
from .utils import blue, highlight_tags, pink


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
    description = CharField()

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
            description=ical_event.get('description', ''),
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

        out = u"{}\t{}\t{}".format(
            blue(start),
            blue(end),
            highlight_tags(self.summary)
        )

        if self.description:
            out += u"\n\t" + pink(format(self.description)).replace("\n", "\n\t")

        return out

    @property
    def start_date(self):
        return self.start.date()

    @property
    def duration_seconds(self):
        return (self.end - self.start).total_seconds()

    @property
    def duration_minutes(self):
        return self.duration_seconds / 60.0

    @property
    def duration_hours(self):
        return self.duration_seconds / (3600.0)

    @property
    def duration_days(self):
        return self.duration_seconds / (3600.0 * 24)

    def get_var(self, varname):
        if hasattr(self, varname):
            return getattr(self, varname)
        else:
            return self.equality_property(varname)

    def equality_property(self, key):
        """
        Extracts a property from the event of the form key=value, e.g. units=3
        """
        try:
            return re.search('\\b%s=(\S+)\\b' % key, self.summary).group(1)
        except (AttributeError):
            raise ValueError("Event {} doesn't match for property {}".format(self, key))

    @property
    def percentage(self):
        # Used for #bodyfat measurements
        return self.measurement_property('percentage', '\\b([0-9.]+)%')

    @property
    def kg(self):
        # Used for #weight measurements
        return self.measurement_property('kg', '([0-9.]+)kg\\b')

    @property
    def mg(self):
        # Used for drug intake, e.g. #caffeine measurements
        return self.measurement_property('mg', '([0-9.]+)mg\\b')

    def measurement_property(self, units, regex):
        """
        Extracts a property from the event description of the form Xunits,
        e.g. 80kg
        """
        try:
            return float(
                re.search(regex, self.summary).group(1)
            )
        except (ValueError, AttributeError):
            raise ValueError("Event {} doesn't match for property {}".format(self, units))


def normalized(dt):
    # Fix the broken API for ical events - dt may be a date or datetime, so
    # make sure it is a datetime
    if not isinstance(dt, datetime):
        dt = datetime.combine(dt, time(0))

    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt
