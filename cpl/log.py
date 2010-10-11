import logging
import threading
import os
import datetime

import CPL_recipe

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('cpl').addHandler(NullHandler())

level = { "DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARNING":logging.WARN, 
          "ERROR":logging.ERROR }

class LogServer(threading.Thread):

    def __init__(self, filename, name, level):
        threading.Thread.__init__(self)
        self.logfile = filename
        self.name = name
        self.level = CplLogger.verbosity.index(level)
        self.entries = LogList()
        os.mkfifo(self.logfile)
        self.start()

    def run(self):
        try:
            logfile = open(self.logfile)
        except:
            pass
        try:
            for line in logfile:
                self.log(line)
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
            record = logging.LogRecord('%s.%s' % (self.name, func), 
                                       lvl, None, None, msg, None, None, func)
            created = float(creation_date.strftime('%s'))
            if record.created < created:
                created -= 86400
            record.relativeCreated -= record.msecs
            record.relativeCreated += 1000*(created - record.created + 1) 
            record.created = created
            record.msecs = 0.0
            self.entries.append(record)
            logging.getLogger('%s.%s' % (self.name, func)).handle(record)
        except:
            pass

class LogList(list):
    '''List of log messages.

    Accessing this list directly will return the :class:`logging.LogRecord`
    instances. To get them formatted as string, use the :attr:`error`,
    :attr:`warning`, :attr:`info` or :attr:`debug` attributes.
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

    verbosity = [ DEBUG, INFO, WARN, ERROR, OFF ]

    _time_enabled = False

    def __init__(self, name = 'cpl'):
        self.name = name

    @property
    def level(self):
        '''Log level for output to the terminal. Any of
        [ DEBUG, INFO, WARN, ERROR, OFF ]

        .. deprecated:: 0.3
           Use :func:`logging.Logger.setLevel` 
        '''
        return CplLogger.verbosity[CPL_recipe.get_msg_level()]

    @level.setter
    def level(self, level):
        CPL_recipe.set_msg_level(CplLogger.verbosity.index(level))

    @property
    def time(self):
        '''Specify whether time tag shall be included in the terminal output

        .. deprecated:: 0.3
           Use :func:`logging.Handler.setFormatter` 
        '''
        return CplLogger._time_enabled

    @time.setter
    def time(self, enable):
        CPL_recipe.set_msg_time(enable);
        CplLogger._time_enabled = not not enable

    @property
    def domain(self):
        '''The domain tag in the header of the log file.

        .. deprecated:: 0.3
           Use :func:`logging.getLogger` 
        '''
        return CPL_recipe.get_log_domain()

    @domain.setter
    def domain(self, domain):
        CPL_recipe.set_log_domain(domain)

    def log(self, level, msg, caller = None):
        if caller == None:
            caller = CPL_recipe.get_log_domain()
        logging.getLogger('%s.%s' % (self.name, caller)).log(level, msg)
        CPL_recipe.log(Logger.verbosity.index(level), caller, msg)

    def debug(self, msg, caller = None):
        '''Put a 'debug' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message.
        :type caller: :class:`str`

        .. deprecated:: 0.3
           Use :func:`logging.Logger.debug` 
        '''
        self.log(CplLogger.DEBUG, msg, caller)

    def info(self, msg, caller = None):
        '''Put an 'info' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message.
        :type caller: :class:`str`

        .. deprecated:: 0.3
           Use :func:`logging.Logger.info` 
        '''
        self.log(CplLogger.INFO, msg, caller)

    def warn(self, msg, caller = None):
        '''Put a 'warn' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message.
        :type caller: :class:`str`

        .. deprecated:: 0.3
           Use :func:`logging.Logger.warn` 
        '''
        self.log(CplLogger.WARN, msg, caller)

    def error(self, msg, caller = None):
        '''Put an 'error' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message.
        :type caller: :class:`str`

        .. deprecated:: 0.3
           Use :func:`logging.Logger.error` 
        '''
        self.log(CplLogger.ERROR, msg, caller)

    def indent_more(self):
        '''Indent the output more.'''
        CPL_recipe.log_indent_more()

    def indent_less(self):
        '''Indent the output less.'''
        CPL_recipe.log_indent_less()

msg = CplLogger()
