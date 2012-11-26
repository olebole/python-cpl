'''`EsoRex <http://www.eso.org/sci/software/cpl/esorex.html>`_ is a standard
execution environment for CPL recipes provided by `ESO <http://www.eso.org>`_.
'''

import os
import cpl
import logging

def load_sof(source):
    '''Read an :program:`EsoRex` SOF file.

    :param source: SOF ("Set Of Files") file object or string with SOF
        file content.
    :type source: :class:`str` or :class:`file`

    These files contain the raw and calibration files for a recipe.  The
    content of the file is returned as a map with the tag as key and the list
    of file names as value.

    The result of this function may directly set as :attr:`cpl.Recipe.calib`
    attribute::
    
      import cpl
      myrecipe = cpl.Recipe('muse_bias')
      myrecipe.calib = cpl.esorex.read_sof(file('muse_bias.sof'))
    
    .. note::

      The raw data frame is silently ignored wenn setting
      :attr:`cpl.Recipe.calib` for MUSE recipes. Other recipes ignore the raw
      data frame only if it was set manually as :attr:`cpl.Recipe.tag` or in
      :attr:`cpl.Recipe.tags` since there is no way to automatically
      distinguish between them.

    '''
    if isinstance(source, str):
        return load_sof(file(source) if os.path.exists(source) else source.split('\n'))
    elif isinstance(source, (file, list)):
        res = dict()
        for line in source:
            if not line or line.startswith('#'):
                continue
            ls = line.split()
            fn = ls[0]
            key = ls[1]
            if key not in  res:
                res[key] = fn
            elif isinstance(res[key], list):
                res[key].append(fn)
            else:
                res[key] = [ res[key], fn ]
        return res
    else:
        raise ValueError('Cannot assign type %s to framelist' % 
                         source.__class__.__name__)

def load_rc(source = None):
    '''Read an :program:`EsoRex` configuration file.

    :param source: Configuration file object, or string with file content. 
                   If not set, the :program:`EsoRex` config file
                   :file:`~/.esorex/esorex.rc` is used.
    :type source: :class:`str` or :class:`file`

    These files contain configuration parameters for :program:`EsoRex` or
    recipes. The content of the file is returned as a map with the (full)
    parameter name as key and its setting as string value.

    The result of this function may directly set as :attr:`cpl.Recipe.param`
    attribute::
    
      import cpl
      myrecipe = cpl.Recipe('muse_bias')
      myrecipe.param = cpl.esorex.load_rc('muse_bias.rc')

    '''
    if source is None:
        source = file(os.path.expanduser('~/.esorex/esorex.rc'))
    if isinstance(source, str):
        return load_rc(file(source) if os.path.exists(source) else source.split('\n'))
    elif isinstance(source, (file, list)):
        res = dict()
        for line in source:
            if not line or not line.strip() or line.startswith('#'):
                continue
            name = line.split('=', 1)[0]
            value = line.split('=', 1)[1]
            if name and value:
                res[name.strip()] = value.strip()
        return res
    else:
        raise ValueError('Cannot assign type %s to parameter list' % 
                         source.__class__.__name__)

def init(source = None):
    '''Set up the logging and the recipe search path from the
    :file:`esorex.rc` file.

    :param source: Configuration file object, or string with file content. 
        If not set, the esorex config file :file:`~/.esorex/esorex.rc` is used.
    :type source: :class:`str` or :class:`file`
    '''

    rc = cpl.esorex.load_rc(source)
    if rc.has_key('esorex.caller.recipe-dir'):
        cpl.Recipe.path = rc['esorex.caller.recipe-dir'].split(':')
    if rc.has_key('esorex.caller.msg-level'):
        msg.level = rc['esorex.caller.msg-level']
    if rc.has_key('esorex.caller.log-level'):
        log.level = rc['esorex.caller.log-level']
    if rc.has_key('esorex.caller.log-dir'):
        log.dir = rc['esorex.caller.log-dir']
    if rc.has_key('esorex.caller.log-file'):
        log.filename = rc['esorex.caller.log-file']

class CplLogger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    OFF = logging.CRITICAL + 1

    def __init__(self, msg = True):
        self.handler = None
        self._component = False
        self._time = False
        self._threadid = False
        self.format = None
        self._filename = None
        self.dir = None
        self._msg = msg
        self._level = CplLogger.OFF

    def _init_handler(self):
        if not self.handler:
            if self._msg:
                self.handler = logging.StreamHandler()
            elif self._filename:
                if self.dir:
                    fname = os.path.join(self.dir, self._filename)
                    self.handler = logging.FileHandler(fname)
                else:
                    self.handler = logging.FileHandler(self._filename)
            else:
                self.handler = None
            if self.handler:
                logging.getLogger().addHandler(self.handler)
                self.handler.setFormatter(logging.Formatter(self.format,
                                                            '%H:%M:%S'))

    def _shutdown_handler(self):
        if self.handler:
            logging.getLogger().removeHandler(self.handler)
            self.handler = None

    @property
    def level(self):
        '''Log level for output to the terminal. Any of
        [ DEBUG, INFO, WARN, ERROR, OFF ].
        '''
        return self._level

    @level.setter
    def level(self, level):
        if isinstance(level, (str, unicode)):
            level = cpl.logger.level[level.upper()]
        if level == CplLogger.OFF:
            self._shutdown_handler()
        else:
            self._init_handler()
            logging.getLogger().setLevel(logging.DEBUG)
            if self.handler:
                self.handler.setLevel(level)
        self._level = level

    @property
    def format(self):
        '''Output format. 

        .. seealso :: `logging.LogRecord attributes <http://docs.python.org/library/logging.html#logrecord-attributes>`_ 

           Key mappings in the logging output.'''
        return self._format

    @format.setter
    def format(self, fmt):
        if fmt == None:
            fmt = '%(asctime)s ' if self._time else ''
            fmt += '[%(levelname)7s]'
            fmt += '[%(threadName)s] ' if self._threadid else ' '
            fmt += '%(name)s: ' if self._component else ''
            fmt += '%(message)s'
        if self.handler:
            self.handler.setFormatter(logging.Formatter(fmt, '%H:%M:%S'))
        self._format = fmt

    @property
    def component(self):
        '''If :obj:`True`, attach the component name to output messages.
        '''
        return self._component

    @component.setter
    def component(self, enable):
        self._component = enable
        self.format = None

    @property
    def time(self):
        '''If :obj:`True`, attach a time tag to output messages.
        '''
        return self._time

    @time.setter
    def time(self, enable):
        self._time = enable
        self.format = None

    @property
    def threadid(self):
        '''If :obj:`True`, attach a thread tag to output messages.
        '''
        return self._threadid

    @threadid.setter
    def threadid(self, enable):
        self._threadid = enable
        self.format = None

    @property
    def filename(self):
        '''Log file name.
        '''
        return self._filename

    @filename.setter
    def filename(self, name):
        if self._msg:
            raise AttributeError('Cannot set file name of message output')
        if self._filename != name:
            self._shutdown_handler()
            self._filename = name
            self._init_handler()

    def __repr__(self):
        return 'cpl.esorex.CplLogger(msg=%s)' % `self._msg`

msg = CplLogger(msg = True)
'''This variable is a :class:`CplLogger` instance that provides a convienience
stream handler similar to the terminal logging functionality of the CPL. It
basically does the same as::

  import logging

  log = logging.getLogger()
  log.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  ch.setFormatter(logging.Formatter('[%(levelname)7s] %(message)s'))
  log.addHandler(ch)
'''

log = CplLogger(msg = False)
'''This variable is a :class:`CplLogger` instance that provides a convienience
file handler similar to the file logging functionality of the CPL. It
basically does the same as::

  import logging

  log = logging.getLogger()
  log.setLevel(logging.INFO)
  ch = logging.FileHandler(filename)
  ch.setLevel(logging.INFO)
  ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)7s] %(funcName)s: %(message)s'))
  log.addHandler(ch)
'''
log.threadid = True
log.component = True
log.time = True
log.level = log.INFO
