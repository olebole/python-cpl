import CPL_recipe

class Logger(object):
    verbosity = [ "debug", "info", "warn", "error", "off" ]

    _time_enabled = False

    def _get_level(self):
        return Logger.verbosity[CPL_recipe.get_msg_level()]

    def _set_level(self, level):
        CPL_recipe.set_msg_level(Logger.verbosity.index(level))

    level = property(_get_level, _set_level)

    def _enable_time(self, enable):
        CPL_recipe.set_msg_time(enable);
        Logger._time_eanbled = not not enable

    time = property(lambda self: Logger._time_enabled, _enable_time)

    def logfile(self, name, level = 'info'):
        CPL_recipe.set_log_file(name)
        CPL_recipe.set_log_level(Logger.verbosity.index(level))

    def _get_file(self):
        return CPL_recipe.get_log_file()

    file = property(_get_file)

    domain = property(lambda self: CPL_recipe.get_log_domain(),
                      lambda self, domain: CPL_recipe.set_log_domain(domain))

    def log(self, level, msg, caller = None):
        if caller == None:
            caller = CPL_recipe.get_log_domain()
        CPL_recipe.log(Logger.verbosity.index(level), caller, msg)

    def debug(self, msg, caller = None):
        self.log("debug", msg, caller)

    def info(self, msg, caller = None):
        self.log("info", msg, caller)

    def warn(self, msg, caller = None):
        self.log("warn", msg, caller)

    def error(self, msg, caller = None):
        self.log("error", msg, caller)

    def indent_more(self):
        CPL_recipe.log_indent_more()

    def indent_less(self):
        CPL_recipe.log_indent_less()

msg = Logger()
