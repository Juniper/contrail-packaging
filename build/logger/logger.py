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

class PackagerLogger(logging.getLoggerClass()):
    def reprint_errors(self):
        if not hasattr(self, 'all_error_records'):
            self.all_error_records = []
        for record in self.all_error_records:
            self.handle(record)
        self.all_error_records = []

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        if level == logging.ERROR:
            if not hasattr(self, 'all_error_records'):
                self.all_error_records = []
            self.all_error_records.append(rv)
        return rv

