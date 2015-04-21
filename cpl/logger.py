from __future__ import absolute_import
import datetime
import logging
import os
import re
import sys
import tempfile
import threading

from . import CPL_recipe

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('cpl').addHandler(NullHandler())

level = { "DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARN, 
          "ERROR":logging.ERROR, "OFF":(logging.CRITICAL + 1)}

cpl_verbosity = [ logging.DEBUG, logging.INFO, logging.WARN,
                  logging.ERROR, logging.CRITICAL + 1 ]

class LogServer(threading.Thread):

    def __init__(self, name, level = None):
        threading.Thread.__init__(self)
        self.name = name
        self.logger = logging.getLogger(name)
        self.level = cpl_verbosity.index(level) if level is not None else 0
        self.entries = LogList()
        self.regexp = re.compile('(\\d\\d):(\\d\\d):(\\d\\d)' +
                                 '\\s\\[\\s*(\\w+)\\s*\\]' + 
                                 '\\s(\\w+):' +
                                 '(\\s\\[tid=(\\d+)\\])?' +
                                 '\\s(.+)')
        tmphdl, self.logfile = tempfile.mkstemp(prefix = 'cpl', suffix='.log')
        os.close(tmphdl)
        os.remove(self.logfile)
        os.mkfifo(self.logfile)
        self.start()

    def run(self):
        try:
            with open(self.logfile, 'rb', buffering = 0) as logfile:
                line = logfile.readline()
                os.remove(self.logfile)
                while line:
                    self.log(str(line.decode('ascii')))
                    line = logfile.readline()
        except:
            pass

    def log(self, s):
        '''Convert CPL log messages into python log records.
        
        A typical CPL log message looks like

         10:35:25 [WARNING] rtest: [tid=000] No file tagged with FLAT

        '''
        try:
            m = self.regexp.match(s)
            if m is not None:
                g = m.groups()
                creation_date = datetime.datetime.combine(
                    datetime.date.today(), 
                    datetime.time(int(g[0]),int(g[1]),int(g[2])))
                lvl = level.get(g[3], logging.NOTSET)
                func = g[4]
                log = logging.getLogger('%s.%s' % (self.logger.name, func))
                threadid = int(g[6]) if g[6] else None
                msg = g[-1]
                record = logging.LogRecord(log.name, lvl, None, None, 
                                           msg, None, None, func)
                created = float(creation_date.strftime('%s'))
                if record.created < created:
                    created -= 86400
                record.relativeCreated -= record.msecs
                record.relativeCreated += 1000*(created - record.created + 1) 
                record.created = created
                record.msecs = 0.0
                record.threadid = threadid
                record.threadName = ('Cpl-%03i' % threadid) if threadid \
                    else 'CplThread'
            elif self.entries:
                r0 = self.entries[-1]
                msg = s.rstrip()
                lvl = r0.levelno
                log = logging.getLogger(r0.name)
                record = logging.LogRecord(r0.name, lvl, None, None, 
                                           msg, None, None, r0.funcName)
                record.relativeCreated = r0.relativeCreated
                record.created = r0.created
                record.msecs = r0.msecs
                record.threadid = r0.threadid
                record.threadName = r0.threadName
            else:
                return
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

