import datetime
import logging
import os
import sys
import tempfile
import threading

import CPL_recipe

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('cpl').addHandler(NullHandler())

level = { "DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARN, 
          "ERROR":logging.ERROR }

class LogServer(threading.Thread):

    def __init__(self, name, level):
        threading.Thread.__init__(self)
        self.name = name
        self.logger = logging.getLogger(name)
        self.level = cpl_verbosity.index(level)
        self.entries = LogList()
        tmphdl, self.logfile = tempfile.mkstemp(prefix = 'cpl', suffix='.log')
        os.close(tmphdl)
        os.remove(self.logfile)
        os.mkfifo(self.logfile)
        self.start()

    def run(self):
        try:
            logfile = open(self.logfile, buffering = 0)
        except:
            pass
        try:
            line = logfile.readline()
            os.remove(self.logfile)
            while line:
                self.log(line)
                line = logfile.readline()
        except:
            pass

    def log(self, s):
        try:
            creation_date = datetime.datetime.combine(
                datetime.date.today(), 
                datetime.time(int(s[0:2]),int(s[3:5]),int(s[6:8])))
            lvl = level.get(s[10:17].strip(), logging.NOTSET)
            func = s[19:].split(':', 1)[0]
            msg = s[19:].split(':', 1)[1][1:-1]
            if msg.startswith('[tid='):
                threadid = int(msg[5:8])
                msg = msg[10:] if threadid > 0 else msg[12:]
            else:
                threadid = None
            log = logging.getLogger('%s.%s' % (self.logger.name, func))
            record = logging.LogRecord(log.name, lvl, None, None, msg, 
                                       None, None, func)
            created = float(creation_date.strftime('%s'))
            if record.created < created:
                created -= 86400
            record.relativeCreated -= record.msecs
            record.relativeCreated += 1000*(created - record.created + 1) 
            record.created = created
            record.msecs = 0.0
            record.threadid = threadid
            record.threadName = ('Cpl-%03i' % threadid) if threadid else 'CplThread'
            self.entries.append(record)
            if log.isEnabledFor(lvl) and log.filter(record):
                log.handle(record)
        except:
            pass

class LogList(list):
    '''List of log messages.

    Accessing this :class:`list` directly will return the
    :class:`logging.LogRecord` instances. 

    Example::

      res = muse_bias(bias_frames)
      for logrecord in res.log:
          print '%s: %s' % (entry.funcname, entry.msg)

    To get them formatted as string, use the :attr:`error`, :attr:`warning`,
    :attr:`info` or :attr:`debug` attributes::

      res = muse_bias(bias_frames)
      for line in res.log.info:
          print line

    '''
    def filter(self, level):
        return [ '%s: %s' % (entry.funcName, entry.msg) for entry in self 
                 if entry.levelno >= level ]

    @property
    def error(self):
        '''Error messages as list of :class:`str`
        '''
        return self.filter(logging.ERROR)

    @property
    def warning(self):
        '''Warnings and error messages as list of :class:`str`
        '''
        return self.filter(logging.WARN)

    @property
    def info(self):
        '''Info, warning and error messages as list of :class:`str`
        '''
        return self.filter(logging.INFO)

    @property
    def debug(self):
        '''Debug, info, warning, and error messages as list of :class:`str`
        '''
        return self.filter(logging.DEBUG)

class CplLogger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    OFF = 101

    def __init__(self):
        self.msg_handler = None
        self._format = '[%(levelname)7s] %(funcName)s: %(message)s'

    def _init_handler(self):
        if not self.msg_handler:
            self.msg_handler = logging.StreamHandler()
            self.msg_handler.setFormatter(logging.Formatter(self.format,
                                                            '%H:%M:%S'))
            logging.getLogger().addHandler(self.msg_handler)

    def _shutdown_handler(self):
        if self.msg_handler:
            logging.getLogger().removeHandler(self.msg_handler)
            self.msg_handler = None

    @property
    def level(self):
        '''Log level for output to the terminal. Any of
        [ DEBUG, INFO, WARN, ERROR, OFF ]
        '''
        return self.msg_handler.level if self.msg_handler else CplLogger.OFF

    @level.setter
    def level(self, level):
        if level == CplLogger.OFF:
            self._shutdown_handler()
        else:
            self._init_handler()
            logging.getLogger().setLevel(logging.DEBUG)
            self.msg_handler.setLevel(level)

    @property
    def format(self):
        '''Output format. 

        See `LogRecord attributes.http://docs.python.org/library/logging.html#logrecord-attributes`_ for a usable key mappings.'''
        return self._format

    @format.setter
    def format(self, fmt):
        self._format = fmt
        self.msg_handler.setFormatter(logging.Formatter(fmt, '%H:%M:%S'))

cpl_verbosity = [ logging.DEBUG, logging.INFO, logging.WARN,
                  logging.ERROR, CplLogger.OFF ]

msg = CplLogger()
lib_version = CPL_recipe.version()
lib_description = CPL_recipe.description()
