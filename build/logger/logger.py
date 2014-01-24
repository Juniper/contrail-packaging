#!/usr/bin/env python
import logging

class SplStreamLoggingFormatter(logging.Formatter):
    simple_format = '[%(asctime)-15s: %(funcName)s] %(message)s'
    long_format   = '\033[00;31m[%(asctime)-15s: %(filename)s:%(lineno)s:%(funcName)s: %(levelname)s]\033[00m %(message)s'
    FORMATS = {logging.DEBUG:   simple_format,
               logging.ERROR:   long_format,
               logging.WARNING: long_format,
               logging.INFO:    simple_format,
               'DEFAULT'   :    simple_format}

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)

class SplFileLoggingFormatter(logging.Formatter):
    simple_format = '[%(asctime)-15s: %(funcName)s: %(levelname)s] %(message)s'
    long_format   = '[%(asctime)-15s: %(filename)s:%(lineno)s:%(funcName)s: %(levelname)s] %(message)s'
    FORMATS = {logging.DEBUG:   simple_format,
               logging.ERROR:   long_format,
               logging.WARNING: long_format,
               logging.INFO:    simple_format,
               'DEFAULT'   :    simple_format}

    def format(self, record):
        self._fmt = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)
