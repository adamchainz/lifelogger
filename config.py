# coding=utf-8
import json
import os
from UserDict import DictMixin

DATA_PATH = os.path.expanduser("~/.config/lifelogger/")
CONFIG_PATH = os.path.join(DATA_PATH, "config.json")


class ConfigDict(DictMixin, object):

    def __init__(self, path):
        self._path = path
        self._loaded = False
        self._data = {}

    def _load(self):
        print "load"
        try:
            with open(self._path) as cfile:
                self._data.update(json.load(cfile))
        except IOError:
            raise IOError("Config file {} missing or corrupt!".format(self._path))

        self._loaded = True

    def _save(self):
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)

        with open(CONFIG_PATH, 'w') as cfile:
            cfile.write(json.dump(self._data))

    def __getitem__(self, key):
        if not self._loaded:
            self._load()
        return self._data[key]

    def __setitem__(self, key, value):
        if not self._loaded:
            self._load()

        self._data[key] = value

        self._save()

config = ConfigDict(CONFIG_PATH)
