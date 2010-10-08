import logging
import threading
import os
import dateutil.parser

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
        os.remove(self.logfile)

    def log(self, s):
        try:
            creation_date = dateutil.parser.parse(s[:8])
            lvl = level.get(s[10:17].strip(), logging.NOTSET)
            func = s[19:].split(':', 1)[0]
            msg = s[19:].split(':', 1)[1][1:-1]
            record = logging.LogRecord('%s.%s' % (self.name, func), 
                                       lvl, None, None, msg, None, None, func)
            created = float(creation_date.strftime('%s'))
            if record.created < created:
                created -= 86400
            record.relativeCreated += created - record.created
            record.created = created
            record.msecs = 0.0
            self.entries.append(record)
            logging.getLogger('%s.%s' % (self.name, func)).handle(record)
        except:
            pass

class LogList(list):
    '''List of log messages.
    '''
    def filter(self, level):
        return [ '%s: %s' % (entry.funcName, entry.msg) for entry in self 
                 if entry.levelno >= level ]

    @property
    def error(self):
        '''Error messages
        '''
        return self.filter(logging.ERROR)

    @property
    def warning(self):
        '''Warnings and error messages
        '''
        return self.filter(logging.WARN)

    @property
    def info(self):
        '''Info, warning and error messages
        '''
        return self.filter(logging.INFO)

    @property
    def debug(self):
        '''Debug, info, warning, and error messages
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

    def level(self):
        '''Log level for output to the terminal. Any of
        [ DEBUG, INFO, WARN, ERROR, OFF ]
        '''
        return CplLogger.verbosity[CPL_recipe.get_msg_level()]

    def _set_level(self, level):
        CPL_recipe.set_msg_level(CplLogger.verbosity.index(level))

    level = property(level, _set_level, doc = level.__doc__)

    def time(self):
        '''Specify whether time tag shall be included in the terminal output'''
        return CplLogger._time_enabled

    def _enable_time(self, enable):
        CPL_recipe.set_msg_time(enable);
        CplLogger._time_enabled = not not enable

    time = property(time, _enable_time, doc = time.__doc__)

    def domain(self):
        '''The domain tag in the header of the log file.'''
        return CPL_recipe.get_log_domain()

    def _set_domain(self, domain):
        CPL_recipe.set_log_domain(domain)
    domain = property(domain, _set_domain, doc = domain.__doc__)

    def log(self, level, msg, caller = None):
        if caller == None:
            caller = CPL_recipe.get_log_domain()
        logging.getLogger('cpl.%s' % caller).log(level, msg)
        CPL_recipe.log(Logger.verbosity.index(level), caller, msg)

    def debug(self, msg, caller = None):
        '''Put a 'debug' message to the log.

:param msg: Message to put
:type msg: :class:`str`
:param caller: Name of the function generating the message.
:type caller: :class:`str`
'''
        self.log(CplLogger.DEBUG, msg, caller)

    def info(self, msg, caller = None):
        '''Put an 'info' message to the log.

:param msg: Message to put
:type msg: :class:`str`
:param caller: Name of the function generating the message.
:type caller: :class:`str`
'''
        self.log(CplLogger.INFO, msg, caller)

    def warn(self, msg, caller = None):
        '''Put a 'warn' message to the log.

:param msg: Message to put
:type msg: :class:`str`
:param caller: Name of the function generating the message.
:type caller: :class:`str`
'''
        self.log(CplLogger.WARN, msg, caller)

    def error(self, msg, caller = None):
        '''Put an 'error' message to the log.

:param msg: Message to put
:type msg: :class:`str`
:param caller: Name of the function generating the message.
:type caller: :class:`str`
'''
        self.log(CplLogger.ERROR, msg, caller)

    def indent_more(self):
        '''Indent the output more.'''
        CPL_recipe.log_indent_more()

    def indent_less(self):
        '''Indent the output less.'''
        CPL_recipe.log_indent_less()

msg = CplLogger()
