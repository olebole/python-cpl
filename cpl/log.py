import CPL_recipe

class Logger(object):
    verbosity = [ "debug", "info", "warn", "error", "off" ]

    _time_enabled = False

    def level(self):
        '''Log level for output to the terminal. Any of
        [ 'debug', 'info', 'warn', 'error', 'off' ]
        '''
        return Logger.verbosity[CPL_recipe.get_msg_level()]

    def _set_level(self, level):
        CPL_recipe.set_msg_level(Logger.verbosity.index(level))

    level = property(level, _set_level, doc = level.__doc__)

    def time(self):
        '''Specify whether time tag shall be included in the terminal output'''
        return Logger._time_enabled

    def _enable_time(self, enable):
        CPL_recipe.set_msg_time(enable);
        Logger._time_enabled = not not enable

    time = property(time, _enable_time, doc = time.__doc__)

    def logfile(self, name, level = 'info'):
        '''Open a logfile with the specified name. 

        :param name: Log file name
        :type name: :class:`str`
        :param level: Log level. Any of 
                      [ 'debug', 'info', 'warn', 'error', 'off' ]
        :type level: :class:`str`

        .. note:: This is possible only once due to limitations of the CPL.
        ''' 
        CPL_recipe.set_log_file(name)
        CPL_recipe.set_log_level(Logger.verbosity.index(level))

    @property
    def file(self):
        '''Get the log file name, if one is set.'''
        return CPL_recipe.get_log_file()

    def domain(self):
        '''The domain tag in the header of the log file.'''
        return CPL_recipe.get_log_domain()

    def _set_domain(self, domain):
        CPL_recipe.set_log_domain(domain)
    domain = property(domain, _set_domain, doc = domain.__doc__)

    def log(self, level, msg, caller = None):
        if caller == None:
            caller = CPL_recipe.get_log_domain()
        CPL_recipe.log(Logger.verbosity.index(level), caller, msg)

    def debug(self, msg, caller = None):
        '''Put a 'debug' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message. 
        :type caller: :class:`str`
        '''
        self.log("debug", msg, caller)

    def info(self, msg, caller = None):
        '''Put an 'info' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message. 
        :type caller: :class:`str`
        '''
        self.log("info", msg, caller)

    def warn(self, msg, caller = None):
        '''Put a 'warn' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message. 
        :type caller: :class:`str`
        '''
        self.log("warn", msg, caller)

    def error(self, msg, caller = None):
        '''Put an 'error' message to the log.

        :param msg: Message to put
        :type msg: :class:`str`
        :param caller: Name of the function generating the message. 
        :type caller: :class:`str`
        '''
        self.log("error", msg, caller)

    def indent_more(self):
        '''Indent the output more.'''
        CPL_recipe.log_indent_more()

    def indent_less(self):
        '''Indent the output less.'''
        CPL_recipe.log_indent_less()

msg = Logger()
