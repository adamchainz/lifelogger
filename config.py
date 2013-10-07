# coding=utf-8
import json
import os

DATA_PATH = os.path.expanduser("~/.lifelogger/")
CONFIG_PATH = os.path.join(DATA_PATH, "config.json")


class ConfigDict(dict):

    @classmethod
    def load(cls):
        config = ConfigDict()

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as cfile:
                loaded = json.load(cfile)
            config.update(loaded)

        return config

    def save(self):
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)

        with open(CONFIG_PATH, 'w') as cfile:
            cfile.write(json.dump(self))

config = ConfigDict.load()
