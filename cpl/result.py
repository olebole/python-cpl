import collections
import os
import signal
import logging

try:
    from astropy.io import fits
except:
    import pyfits as fits

class Result(object):
    def __init__(self, recipedefs, dir, res, input_len = 0, logger = None, 
                 output_format = fits.HDUList):
        '''Build an object containing all result frames.

        Calling :meth:`cpl.Recipe.__call__` returns an object that contains
        all result ('production') frames in attributes. All results for one
        tag are summarized in one attribute of the same name. 

        If the argument `output_format` is :class:`astropy.io.fits.HDUList`
        (default), then the attribute content is either a
        :class:`astropy.io.fits.HDUList` or a class:`list` of HDU lists,
        depending on the recipe and the call: If the recipe produces one out
        put frame of a tag per input file, the attribute contains a list if
        the recipe was called with a list, and if the recipe was called with a
        single input frame, the result attribute will also contain a single
        input frame. If the recipe combines all input frames to one output
        frame, a single :class:`astropy.io.fits.HDUList` es returned,
        independent of the input parameters.

        Similarly, if the argument `output_format` is set to :class:`str`, the
        attribute content is either a :class:`str` or a class:`list` of
        :class:`str`, containing the paths of output files. In this case,
        removing the output files is suppressed.

        .. todo:: This behaviour is made on some heuristics based on the
           number and type of the input frames. The heuristics will go wrong
           if there is only one input frame, specified as a list, but the
           recipe tries to summarize the input. In this case, the attribute
           will contain a list where a single :class:`astropy.io.fits.HDUList`
           was expected. To solve this problem, the "MASTER" flag has to be
           forwarded from the (MUSE) recipe which means that it should be
           exported by the recipe -- this is a major change since it probably
           leads into a replacement of CPLs recipeconfig module by something
           more sophisticated. And this is not usable for non-MUSE recipes
           anyway. So, we will skip this to probably some distant future.
        '''
        self.dir = os.path.abspath(dir)
        logger.join()
        if res[2][0]:
            raise CplError(res[2][0], res[1], logger)
        self.tags = set()
        for tag, frame in res[0]:
            if (output_format == fits.HDUList): 
                # Move the file to the base dir to avoid NFS problems
                outframe = os.path.join(
                    os.path.dirname(self.dir), 
                    '%s.%s' % (os.path.basename(self.dir), frame))
                os.rename(os.path.join(self.dir, frame), outframe)
            else:
                outframe = os.path.join(self.dir, frame)
            if output_format == fits.HDUList:
                hdulist = fits.open(outframe, memmap = True, mode = 'update')
                hdulist.readall()
                os.remove(outframe)
                outframe = hdulist
            tag = tag
            if tag not in self.__dict__:
                self.__dict__[tag] = outframe if input_len != 1 \
                    else [ outframe ]
                self.tags.add(tag)
            elif isinstance(self.__dict__[tag], (fits.HDUList, str)):
                self.__dict__[tag] = [ self.__dict__[tag], outframe ]
            else:
                self.__dict__[tag].append(outframe)
        mtracefname = os.path.join(self.dir, 'recipe.mtrace')
        mtrace = None
        if os.path.exists(mtracefname):
            try:
                mtrace = os.popen("mtrace %s" % mtracefname).read();
            except:
                mtrace = None
        self.stat = Stat(res[2], mtrace)
        self.error = CplError(res[2][0], res[1], logger) if res[1] else None
        self.log = logger.entries if logger else None

    def __getitem__(self, key):
        if key in self.tags:
            return self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key):
        return key in self.tags

    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        return iter((key, self.__dict__[key]) for key in self.tags)

class Stat(object):
    def __init__(self, stat, mtrace):
        self.return_code = stat[0]
        self.user_time = stat[1]
        self.sys_time = stat[2]
        self.memory_is_empty = { -1:None, 0:False, 1:True }[stat[3]]
        self.mtrace = mtrace;

class CplError(Exception):
    '''Error message from the recipe.

    If the CPL recipe invocation returns an error, it is converted into a
    :class:`cpl.CplError` exception and no frames are returned. Also, the
    error is notified in the log file.

    The exception is raised on recipe invocation, or when accessing the result
    frames if the recipe was started in background
    (:attr:`cpl.Recipe.threaded` set to :obj:`True`).

    Attributes:

    .. attribute:: code

       The CPL error code returned from the recipe.

    .. attribute:: msg

       The supplied error message. 
    
    .. attribute:: filename

       The source file name where the error occurred.

    .. attribute:: line

       The line number where the error occurred.

    .. attribute:: log

       Log lines of the recipe that lead to this exception.

       .. seealso:: :class:`cpl.logger.LogList`

    .. attribute:: next
     
       Next error, or :obj:`None`.

    '''
    def __init__(self, retval, res, logger = None):
        self.retval = retval
        self.log = logger.entries if logger else None
        self.next = None
        if not res:
            self.code, self.msg, self.file, self.line, self.function = (
                None, None, None, None, None)
        else:
            self.code, self.msg, self.file, self.line, self.function = res[0]
            o = self
            for r in res[1:]:
                o.next = CplError(retval, [ r ], logger)
                o = o.next
    
    def __iter__(self):
        class Iter:
            current = self
            def next(self):
                if Iter.current is None:
                    raise StopIteration
                s = Iter.current
                Iter.current = Iter.current.next
                return s
        return Iter()

    def __str__(self):
        if self.code is None:
            s = 'Unspecified'
        else:
            s = "%s (%i) in %s() (%s:%i)" % (self.msg, self.code, 
                                             self.function, self.file, 
                                             self.line) 
        if self.next:
            for e in self.next:
                s += "\n    %s (%i) in %s() (%s:%i)" % (e.msg, e.code, 
                                                        e.function, e.file, 
                                                        e.line) 
        return s

class RecipeCrash(Exception):
    '''Recipe crash exception

    If the CPL recipe crashes with a SIGSEV or a SIGBUS, the C stack trace is
    tried to conserved in this exception. The stack trace is obtained with the
    GNU debugger gdb. If the debugger is not available, or if the debugger
    cannot be attached to the crashed recipe, the Exception remains empty.

    When converted to a string, the Exception will return a stack trace
    similar to the Python stack trace.

    The exception is raised on recipe invocation, or when accessing the result
    frames if the recipe was started in background
    (:attr:`cpl.Recipe.threaded` set to :obj:`True`).

    Attributes:

    .. attribute:: elements

       List of stack elements, with the most recent element (the one that
       caused the crash) at the end. Each stack element is a 
       :func:`collections.namedtuple` with the following attributes:

       .. attribute:: filename
 
          Source file name, including full path, if available.

       .. attribute:: line

          Line number, if available

       .. attribute:: func

          Function name, if available

       .. attribute:: params

          Dictionary parameters the function was called with.  The key here is
          the parameter name, the value is a string describing the value set.

       .. attribute:: localvars

          Dictionary of local variables of the function, if available.  The
          key here is the parameter name, the value is a string describing the
          value set.

    .. attribute:: signal

          Signal that caused the crash.
    '''

    StackElement = collections.namedtuple('StackElement', 
                                          'filename line func params localvars')
    signals = {signal.SIGSEGV:'SIGSEV: Segmentation Fault', 
               signal.SIGBUS:'SIGBUS: Bus Error',
               signal.SIGHUP:'SIGHUP: Hangup',
               signal.SIGABRT:'SIGABRT: Abnormal process termination',
               signal.SIGTERM:'SIGTERM: Terminated by user',
               signal.SIGQUIT:'SIGQUIT: Quit',
               signal.SIGFPE:'SIGFPE: Arithmetic Exception',
               signal.SIGINT:'SIGINT: Interrupt (Ctrl-C)',
               None:'Memory inconsistency detected'}
    def __init__(self, bt_file):
        self.elements = []
        current_element = None
        parse_functions = True
        parse_sourcelist = False
        sourcefiles = dict()
        self.signal = None
        self.lines = []
        for line in bt_file:
            self.lines.append(line)
            if line.startswith('Received signal:'):
                self.signal = int(line.split(':')[1])
            if line.startswith('Memory corruption'):
                self.signal = None
            elif line.find('signal handler called') >= 0:
                del self.elements[:]
            elif parse_functions:
                if line.startswith('#'):
                    try:
                        current_element = self._parse_function_line(line)
                    except StopIteration:
                        parse_functions = False
                elif current_element is not None:
                    self._add_variable(current_element.localvars, line)
            if line.startswith('Source files'):
                parse_sourcelist = True
                parse_functions = False
            elif parse_sourcelist:
                sourcefiles.update(dict((os.path.basename(s.strip()), s.strip())
                                        for s in line.split(',') 
                                        if s.rfind('/') > 0 ))
        self.elements = [ RecipeCrash.StackElement(sourcefiles.get(e.filename, 
                                                                   e.filename),
                                                   e.line, e.func, e.params, 
                                                   e.localvars) 
                          for e in self.elements ]
        Exception.__init__(self, str(self))

    def _add_variable(self, vars, line):
        s = line.strip().split('=', 1)
        if len(s) > 1:
            vars[s[0].strip()] = s[1].strip()

    def _parse_function_line(self, line):
        s = line.split()
        funcname = s[3] if s[1].startswith('0x') else s[1]
        if funcname.startswith('Py'):
            raise StopIteration()
        pars = {}
        for fp in line[line.find('(')+1:line.rfind(')')].split(','):
            self._add_variable(pars, fp)
        l = line[line.rfind(')')+1:].split()
        if not l:
            return None
        source = l[-1].split(':')
        filename = source[0]
        lineno = int(source[1]) if len(source) > 1 else None
        current_element = RecipeCrash.StackElement(filename, lineno, 
                                                   funcname, pars, {})
        self.elements.insert(0, current_element)
        return current_element
        
    def log(self, logger):
        '''Put the content of the crash into the log.
        '''
        log = logging.getLogger('%s' % logger.name)
        log.error('Recipe crashed. Traceback (most recent call last):')
        for e in self.elements:
            logc = logging.getLogger('%s.%s' % (logger.name, e.func))
            logc.error('  File "%s", %sin %s\n' % (
                    e.filename, 
                    'line %i, ' % e.line if e.line else '', 
                    e.func))
            if os.path.exists(e.filename) and e.line:
                logc.error('    %s\n' 
                           % open(e.filename).readlines()[e.line-1].strip())
            if e.params:
                logc.error('  Parameters:')
                for p, v in e.params.items():
                    logc.error('    %s = %s' % (p, v))
            if e.localvars:
                logc.error('  Local variables:')
                for p, v in e.localvars.items():
                    logc.error('    %s = %s' % (p, v))
        log.error(RecipeCrash.signals.get(self.signal, 
                                          '%s: Unknown' % str(self.signal)))

    def __repr__(self):
        return 'RecipeCrash()'

    def __str__(self):
        s = 'Recipe Traceback (most recent call last):\n'
        for e in self.elements:
            s += '  File "%s", %sin %s\n' % ((e.filename), 
                                             'line %i, ' % e.line if e.line 
                                             else '', 
                                             e.func)
            if os.path.exists(e.filename) and e.line:
                s += '    %s\n' % open(e.filename).readlines()[e.line-1].strip()
        s += RecipeCrash.signals.get(self.signal, '%s: Unknown' % str(self.signal))
        return s

