#!/usr/bin/env python
# coding=utf-8
import sys

from lifelogger.main import main


if __name__ == '__main__':
    success = main(sys.argv)
    sys.exit(0 if success else 1)
