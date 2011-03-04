import os
import tempfile
import threading
import collections
import signal

import pyfits
import CPL_recipe
import esorex
from frames import FrameList, Result
from frames import mkabspath, expandframelist
from parameters import ParameterList
from log import LogServer, msg

class Recipe(object):
    '''Pluggable Data Reduction Module (PDRM) from a ESO pipeline. 

    Recipes are loaded from shared libraries that are provided with the
    pipeline library of the instrument.

    The libraries are searched in the directories specified by the class
    attribute :attr:`Recipe.path` or its subdirectories. The search path is
    automatically set to the esorex path when :func:`cpl.esorex.init()`
    is called.

    Attributes:

    name: Recipe name
    filename: Shared library file name
    param: Parameter list
    calib: Calibration frame list
    tag: default tag
    tags: list of possible tags
    author: (author, email) pair
    description: (synopsis, description) pair
    version: (versionnumber, versionstring) pair
    '''

    path = [ '.' ]

    def __init__(self, name, filename = None, version = None, threaded = False):
        '''Try to load a recipe with the specified name in the directory
        specified by the class attribute :attr:`Recipe.path` or its 
        subdirectories.

        :param name: Name of the recipe. Required. Use
            :func:`cpl.Recipe.list()` to get a list of available recipes.
        :type name: :class:`str`

        :param filename:   Name of the shared library. Optional. If not set, 
            :attr:`Recipe.path` is searched for the library file. 
        :type filename: :class:`str`
        :param version: Version number. Optional. If not set, the newest 
            version is loaded.
        :type version: :class:`int` or :class:`str`
        :param threaded: Run the recipe in the background, returning 
            immediately after calling it. Default is :attr:`False`. This may 
            be also set as an attribute or specified as a parameter when 
            calling the recipe. 
        :type threaded: :class:`bool`

        '''
        self._recipe = None
        self.name = name
        if not filename:
            filename = Recipe.get_recipefilename(name, version)
        self.filename = filename
        self._recipe = CPL_recipe.recipe(filename, name)
        if version and version not in self.version:
            raise IOError('wrong version %s (requested %s) for %s in %s' %
                          (str(self.version), str(version), name, filename))
        self._param = ParameterList(self)
        self._calib = FrameList(self)
        self._tags = None
        self.tag = self.tags[0] if self.tags else None
        self.output_dir = None
        self.temp_dir = '.'
        self.threaded = threaded

    def reload(self):
        '''Reload the recipe. 

        All recipe settings remain unchanged.
        '''
        self._recipe = CPL_recipe.recipe(self.filename, self.name)

    @property
    def author(self):
        '''Pair (author name, author email address) of two strings.'''
        return self._recipe.author()

    @property
    def description(self):
        '''Pair (synopsis, description) of two strings.'''
        return self._recipe.description()

    @property
    def version(self):
        '''Pair (versionnumber, versionstring) of an integer and a string. 
        The integer will be increased on development progress.'''
        return self._recipe.version()

    @property
    def copyright(self):
        '''Copyright string'''
        return self._recipe.copyright()

    @property
    def tags(self):
        '''Possible tags for the raw input frames, or ':attr:`None` if this
        information is not provided by the recipe.'''
        frameconfig = self._recipe.frameConfig()
        return [ c[0][0] for c in frameconfig ] if frameconfig else self._tags

    @tags.setter
    def tags(self, t):
        if self._recipe.frameConfig():
            raise AttributeError('Tags are immutable')
        else:
            self._tags = t

    @property
    def tag(self):
        '''Default raw input frame tag. After creation, it is set to the first
        tag from the "tags" property and may be changed to any of these
        tags. If the recipe does not provide the tag information, it must be
        set manually, or the tag name has to be provided when calling the
        recipe.'''
        return self._tag

    @tag.setter
    def tag(self, t):
        if self.tags is None or t in self.tags:
            self._tag = t 
        else:
            raise KeyError("Tag '%s' not in %s" % (t, str(self.tags)))

    @property
    def calib(self):
        '''This attribute contains the calibration frames
        for the recipe.  It is iterable and then returns all calibration frames:
        
        >>> for f in muse_scibasic.calib:
        ...     print f.tag, f.min, f.max, f.files
        TRACE_TABLE 1 1 None
        WAVECAL_TABLE 1 1 None
        MASTER_BIAS 1 1 master_bias_0.fits
        MASTER_DARK None 1 None
        GEOMETRY_TABLE 1 1 None
        BADPIX_TABLE None None ['badpix_1.fits', 'badpix_2.fits']
        MASTER_FLAT None 1 None

        .. note:: Only MUSE recipes are able to provide the full list of
           calibration frames and the minimal/maximal number of calibration
           frames. For other recipes, only frames that were set by the users are
           returned here. Their minimum and maximum value will be set to
           :attr:`None`.

        In order to assing a FITS file to a tag, the file name or the
        :class:`pyfits.HDUList` is assigned to the calibration attribute:

        >>> muse_scibasic.calib.MASTER_BIAS = 'MASTER_BIAS_0.fits'

        Using :class:`pyfits.HDUList` is useful when it needs to be patched
        before fed into the recipe. 

        >>> master_bias = pyfits.open('master_bias_0.fits')
        >>> master_bias[0].header['HIERARCH ESO DET CHIP1 OUT1 GAIN'] = 2.5
        >>> muse_scibasic.calib.MASTER_BIAS = 'master_bias_0.fits'

        Note that :class:`pyfits.HDUList` objects are stored in temporary
        files before the recipe is called which may produce some
        overhead. Also, the CPL then assigns the random temporary file names
        to the FITS keywords ``HIERARCH ESO PRO RECm RAWn NAME`` which should
        be corrected afterwards if needed. 

        To assign more than one frame, put them into a list:

        >>> muse_scibasic.calib.BADPIX_TABLE = [ 'badpix1.fits', 'badpix2.fits' ]
     
        All calibration frames can be set in one step by assigning a
        :class:`dict` to the parameters. In this case, frame that are not in
        the map are set are removed from the list, and unknown frame tags are
        silently ignored. The key of the map is the tag name; the values are
        either a string, or a list of strings, containing the file name(s) or
        the :class:`pyfits.HDUList` objects.

        >>> muse_scibasic.calib = { 'MASTER_BIAS':'master_bias_0.fits', 
        ...                'BADPIX_TABLE':[ 'badpix_1.fits', 'badpix_2.fits' ] }
        '''
        return self._calib

    @calib.setter
    def calib(self, source = None):
        if isinstance(source, (str, file)):
            source = esorex.load_sof(source)
        self._calib = FrameList(self, source) 

    @calib.deleter
    def calib(self):
        self._calib = FrameList(self, None)

    @property
    def param(self):
        '''This attribute contains all recipe parameters. 
        It is iteratable and then returns all individual parameters:

        >>> for p in muse_scibasic.param:
        ...    print p.name, p.value, p.default
        ...
        nifu None 99
        cr None dcr
        xbox None 15
        ybox None 40
        passes None 2
        thres None 4.5
        sample None False
        dlambda None 1.2

        On interactive sessions, all parameter settings can be easily printed by
        printing the :attr:`param` attribute of the recipe:

        >>> print muse_scibasic.param
         [Parameter('nifu', default=99), Parameter('cr', default=dcr), 
          Parameter('xbox', default=15), Parameter('ybox', default=40), 
          Parameter('passes', default=2), Parameter('thres', default=4.5), 
          Parameter('sample', default=False), Parameter('dlambda', default=1.2)]

        To set the value of a recipe parameter, the value can be assigned to
        the according attribute:

        >>> muse_scibasic.param.nifu = 1

        The new value is checked against parameter type, and possible value
        limitations provided by the recipe. Dots in parameter names are
        converted to underscores. In a recipe call, the same parameter can be
        specified as

        >>> res = muse_scibasic( ..., param_nifu = 1)

        To reset a value to its default, it is either deleted, or set to
        :attr:`None`. The following two lines:

        >>> muse_scibasic.param.nifu = None
        >>> del muse_scibasic.param.nifu

        will both reset the parameter to its default value. 

        All parameters can be set in one step by assigning a :class:`dict` to
        the parameters. In this case, all values that are not in the map are
        reset to default, and unknown parameter names are ignored. The keys of
        the map may contain contain the name or the fullname with context:

        >>> muse_scibasic.param = { 'nifu':1, 'xbox':11, 'resample':True }
        '''
        return self._param

    @param.setter
    def param(self, source = None):
        if isinstance(source, (str, file)):
            source = esorex.load_rc(source)
        self._param = ParameterList(self, source)

    @param.deleter
    def param(self):
        self._param = ParameterList(self, None)

    def output(self, tag = None):
        '''Return the list of output frame tags.

        If the recipe does not provide this information, an exception is raised.
        
        :param tag: Input (raw) frame tag. Defaults to the :attr:`Recipe.tag` 
            attribute if not specified. 
        :type tag: :class:`str`
        '''
        if tag is None:
            tag = self.tag
        for c in self._recipe.frameConfig():
            if tag == c[0][0]:
                return c[2]

    def __call__(self, *data, **ndata):
        '''Call the recipes execution with a certain input frame.
        
        :param data:       Data input frames, using the default tag.
        :type data: :class:`pyfits.HDUlist` or :class:`str` or a :class:`list` 
            of them.
        :param tag: Overwrite the :attr:`tag` attribute (optional).
        :type tag: :class:`str`
        :param raw_name = data: Data with a specific tag 'name'.
        :param threaded: overwrite the :attr:`threaded` attribute (optional).
        :type threaded: :class:`bool`
        :param loglevel: set the log level for python :mod:`logging` (optional).
        :type loglevel: :class:`int`
        :param logname: set the log name for the used python 
            :class:`logging.Logger` (optional, default is 'cpl.' + recipename).
        :type logname: :class:`str`
        :param param: overwrite the CPL parameters of the recipe specified
            as keys with their dictionary values (optional). 
        :type param: :class:`dict`
        :param calib: Overwrite the calibration frame lists for the tags 
            specified as keys with their dictionary values (optional).
        :type calib: :class:`dict`
        :return: The object with the return frames as :class:`pyfits.HDUList` 
            objects
        :rtype: :class:`cpl.Result`
        :raise: :class:`exceptions.ValueError` If the invocation parameters 
                are incorrect.
        :raise: :class:`exceptions.IOError` If the temporary directory could 
                not be built, the recipe could not start or the files could not 
                be read/written. This error is also raised if the recipe crashed
                by a segementation fault or similar.
        :raise: :class:`cpl.CplError` If the recipe returns an error.

        .. note:: If the recipe is executed in the background 
            (``threaded = True``) and an exception occurs, this exception is 
            raised whenever result fields are accessed.
        '''
        tmpfiles = []
        recipe_dir = self.output_dir or ( 
            tempfile.mkdtemp(dir = self.temp_dir, 
                             prefix = self.name + "-") 
            if self.temp_dir else os.getcwd())
        threaded = ndata.get('threaded', self.threaded)
        loglevel = ndata.get('loglevel', msg.DEBUG)
        logname = ndata.get('logname', 'cpl.%s' % self.name)
        parlist = self.param._aslist(**ndata)
        raw_frames = self._get_raw_frames(*data, **ndata)
        if len(raw_frames) < 1:
            raise ValueError('No raw frames specified.')
        if len(raw_frames) > 1:
            raise ValueError('More than one raw frame tag specified: %s', 
                            str(raw_frames))
        input_len = -1 if isinstance(raw_frames[0][1], pyfits.HDUList) else \
            len(raw_frames[0][1]) if isinstance(raw_frames[0][1], list) else -1
        calib_frames = self.calib._aslist(**ndata)
        framelist = expandframelist(raw_frames + calib_frames)
        logger = None
        try:
            if (not os.access(recipe_dir, os.F_OK)):
                os.makedirs(recipe_dir)
            tmpfiles = mkabspath(framelist, recipe_dir)
            logger = LogServer(os.path.join(recipe_dir, 'log'), logname,
                               loglevel)
        except:
            self._cleanup(recipe_dir, tmpfiles, logger)
            raise
        return self._exec(recipe_dir, parlist, framelist, input_len, 
                          tmpfiles, logger) \
            if not threaded else \
            Threaded(self._exec, recipe_dir, parlist, framelist, input_len, 
                     tmpfiles, logger)

    def _exec(self, recipe_dir, parlist, framelist, input_len, 
              tmpfiles, logger):
        try:
            return Result(self._recipe.frameConfig(), recipe_dir,
                          self._recipe.run(recipe_dir, parlist, framelist,
                                           logger.logfile, logger.level),
                          (self.temp_dir and not self.output_dir),
                          input_len, logger)
        finally:
            self._cleanup(recipe_dir, tmpfiles, logger)

    def _get_raw_frames(self, *data, **ndata):
        '''Return the input frames.

        Returns a :class:`list` with (tag, the input frame(s)) pairs. Note
        that more than one input tag is not allowed here.
        '''
        m = { }
        tag = ndata.get('tag', self.tag)
        if tag is None:
            if data:
                raise ValueError('No raw input tag')
        else:
            for f in data:
                if self.tag not in m:
                    m[tag] = f
                elif isinstance(m[tag], list) \
                        and not isinstance(m[tag], pyfits.HDUList):
                    m[tag].append(f)
                else:
                    m[tag] = [ m[tag], f ]

        if ndata is not None:
            for name, tdata in ndata.items():
                if name.startswith('raw_'):
                    tag = name.split('_', 1)[1]
                    m[tag] = tdata

        return list(m.iteritems())

    def _cleanup(self, recipe_dir, tmpfiles, logger):
        for f in tmpfiles:
            os.remove(f)
        if logger is not None:
            os.remove(logger.logfile)
        bt = os.path.join(recipe_dir, 'recipe.backtrace')
        if os.path.exists(bt):
            ex = RecipeCrash(bt)
            os.remove(bt)
        else:
            ex = None
        if self.temp_dir and not self.output_dir:
            try:
                os.rmdir(recipe_dir)
            except:
                pass
        if ex:
            raise ex

    @property
    def __doc__(self):
        s = '%s\n\n%s\n\n' % (self.description[0], self.description[1])
        
        r = 'Parameters:\n' 
        maxlen = max(len(p.name) for p in self.param)
        for p in self.param:
            r += ' %s: %s (default: %s)\n' % (
                p.name.rjust(maxlen), p.__doc__, str(p.default))
        r += '\n'
        if self._recipe.frameConfig() is not None:
            c = 'Calibration frames: %s\n\n' % str([f.tag for f in self.calib])
        else:
            c = ''
        if self.tags is not None:
            t = 'Raw and product frames:\n'
            maxlen = max(len(f) for f in self.tags)
            for f in self.tags:
                t += ' %s --> %s\n' % (f.rjust(maxlen), str(self.output(f)))
        else:
            t = ''
        return s + r + c + t + '\n\n'

    def __repr__(self):
        return "Recipe('%s')" % self.name

    @staticmethod
    def list():
        '''Return a list of recipes.
        
        Searches for all recipes in in the directory specified by the class
        attribute :attr:`Recipe.path` or its subdirectories. 
        '''
        plugins = collections.defaultdict(list)
        for f in Recipe.get_libs():
            plugin_f = CPL_recipe.list(f)
            if plugin_f:
                for p in plugin_f:
                    plugins[p[0]].append(p[2])
        return list(plugins.items())

    @staticmethod
    def get_recipefilename(name, version = None):
        filename = None
        rversion = -1
        for f in Recipe.get_libs():
            plugin_f = CPL_recipe.list(f)
            if plugin_f:
                for p in plugin_f:
                    if p[0] != name:
                        continue
                    if version in p[1:3]:
                        return f
                    if rversion < p[2]:
                        rversion = p[2]
                        filename = f
        return filename

    @staticmethod
    def get_libs():
        libs = [ ]
        path = Recipe.path.split(':') if isinstance(Recipe.path, str) else Recipe.path
        for p in path:
            for root, dir, files in os.walk(p):
                libs += [ os.path.join(root, f) 
                           for f in files if f.endswith('.so') ]
        return libs

    @staticmethod
    def set_maxthreads(n):
        '''Set the maximal number of threads to be executed in parallel.

        .. note:: This affects only threads that are started afterwards with
            the ``threaded = True`` flag.
        '''
        Threaded.set_maxthreads(n)

class Threaded(threading.Thread):
    '''Simple threading interface. 

    Creating this object will start the execution of func(*args, **nargs).
    It returns an object that has the same attribute as the function return
    value, if the function execution was completed.

    Accessing any of the attributes will cause a wait until the function
    execution is ready. Note that the attribute delegation will work only for
    attributes (not for methods), and it will not work for attributes defined
    by the threading.Thread interface.

    If the function returns an exception, this exception is thrown by any
    attempt to access an attribute.
    '''
    pool_sema = threading.BoundedSemaphore(65536)

    def __init__(self, func, *args, **nargs):
        threading.Thread.__init__(self)
        self._func = func
        self._args = args
        self._nargs = nargs
        self._res = None
        self._exception = None
        self.start()
                    
    def run(self):
        with Threaded.pool_sema:
            try:
                self._res = self._func(*self._args, **self._nargs)
            except Exception as exception:
                self._exception = exception

    def __getattr__(self, name):
        self.join()
        if self._exception is None:
            return self._res.__dict__[name]
        else:
            raise self._exception

    @staticmethod
    def set_maxthreads(n):
        with Threaded.pool_sema:
            Threaded.pool_sema = threading.BoundedSemaphore(n)

class RecipeCrash(StandardError):
    StackElement = collections.namedtuple('StackElement', 
                                          'filename line func localvars')
    signals = {signal.SIGSEGV:'SIGSEV: Segmentation Fault', 
               signal.SIGBUS:'SIGBUS: Bus Error',
               signal.SIGHUP:'SIGHUP: Hangup',
               signal.SIGQUIT:'SIGQUIT: Quit',
               signal.SIGFPE:'SIGFPE: Arithmetic Exception',
               signal.SIGINT:'SIGINT: Interrupt'}
    def __init__(self, fname):
        self.elements = []
        current_element = None
        handler_found = False
        sourcefiles_found = False
        sourcefiles = dict()
        self.signal = None
        for line in file(fname):
            if line.startswith('Received signal:'):
                self.signal = int(line.split(':')[1])
            elif handler_found:
                if line.startswith('#'):
                    s = line.split()
                    if s[3].startswith('Py'):
                        handler_found = False
                    else:
                        try:
                            s = line.split()
                            filename = s[-1].split(':')[0]
                            lineno = int(s[-1].split(':')[1])
                            current_element = RecipeCrash.StackElement(
                                filename, lineno, s[3], {})
                            self.elements.insert(0, current_element)
                        except:
                            current_element = None
                elif current_element is not None:
                    s = line.strip().split('=', 1)
                    if len(s) > 1:
                        current_element.localvars[s[0].strip()] = s[1].strip()
            elif line.find('signal handler called') >= 0:
                handler_found = True
            elif line.startswith('Source files'):
                sourcefiles_found = True
            elif sourcefiles_found:
                sourcefiles.update(dict((os.path.basename(s.strip()), s.strip()) 
                                        for s in line.split(',') 
                                        if s.rfind('/') > 0 ))
        self.elements = [ RecipeCrash.StackElement(sourcefiles.get(e.filename, 
                                                                   e.filename),
                                                   e.line, e.func, e.localvars) 
                          for e in self.elements ]
        StandardError.__init__(self, str(self))
        
    def __str__(self):
        s = 'Recipe Traceback (most recent call last):\n'
        for e in self.elements:
            s += '  File "%s", line %i, in %s\n' % ((e.filename), 
                                                    e.line, e.func)
            if os.path.exists(e.filename):
                s += '    %s\n' % file(e.filename).readlines()[e.line-1].strip()
        s += RecipeCrash.signals.get(self.signal, '%s: Unknown' % str(self.signal))
        return s

