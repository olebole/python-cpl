import os
import shutil
import tempfile
import threading
import collections

import pyfits
import CPL_recipe
import esorex
from frames import FrameList, mkabspath, expandframelist
from result import Result, RecipeCrash
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

    __name__: Recipe name
    __filename__: Shared library file name
    param: Parameter list
    calib: Calibration frame list
    tag: default tag
    tags: list of possible tags
    __author__: author name
    __email__: author's email address
    description: (synopsis, description) pair
    version: (versionnumber, versionstring) pair
    memory_dump: If set to 1, a memory dump is issued to stdout if the memory was not
      totally freed after the execution. If set to 2, the dump is always issued.
      Standard is 0: nothing dumped.
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
        self.__name__ = name
        if not filename:
            filename = Recipe.get_recipefilename(name, version)
            if not filename:
                raise IOError('Recipe %s not found at path %s' 
                              % (`name`, `Recipe.path`))
        self.__file__ = filename
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
        self.memory_dump = 0
        self.threaded = threaded

    def reload(self):
        '''Reload the recipe. 

        All recipe settings remain unchanged.
        '''
        self._recipe = CPL_recipe.recipe(self.__file__, self.__name__)

    @property
    def __author__(self):
        '''Author name'''
        return self._recipe.author()[0]

    @property
    def __email__(self):
        '''Author email'''
        return self._recipe.author()[1]

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
    def __version__(self):
        return self._recipe.version()[1]

    @property
    def __copyright__(self):
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
            raise KeyError("Tag %s not in %s" % (`t`, str(self.tags)))

    @property
    def calib(self):
        '''This attribute contains the calibration frames
        for the recipe.  It is iterable and then returns all calibration frames:
        
        >>> for f in muse_scibasic.calib:
        ...     print f.tag, f.min, f.max, f.frames
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
        
        :param raw: Data input frames.
        :type raw: :class:`pyfits.HDUlist` or :class:`str` or a :class:`list` 
            of them, or :class:`dict`
        :param tag: Overwrite the :attr:`tag` attribute (optional).
        :type tag: :class:`str`
        :param threaded: overwrite the :attr:`threaded` attribute (optional).
        :type threaded: :class:`bool`
        :param loglevel: set the log level for python :mod:`logging` (optional).
        :type loglevel: :class:`int`
        :param logname: set the log name for the python
            :class:`logging.Logger` (optional, default is 'cpl.' + recipename).
        :type logname: :class:`str`
        :param output_dir: Set or overwrite the :attr:`output_dir` attribute.
        :type output_dir: :class:`str`
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
        threaded = ndata.get('threaded', self.threaded)
        loglevel = ndata.get('loglevel', msg.DEBUG)
        logname = ndata.get('logname', 'cpl.%s' % self.__name__)
        output_dir = ndata.get('output_dir', self.output_dir)
        output_format = str if output_dir else pyfits.HDUList
        if output_dir is None:
            output_dir = tempfile.mkdtemp(dir = self.temp_dir, 
                                          prefix = self.__name__ + "-") 
        parlist = self.param._aslist(ndata.get('param'))
        raw_frames = self._get_raw_frames(*data, **ndata)
        if len(raw_frames) < 1:
            raise ValueError('No raw frames specified.')
        input_len = -1 if isinstance(raw_frames[0][1], pyfits.HDUList) else \
            len(raw_frames[0][1]) if isinstance(raw_frames[0][1], list) else -1
        calib_frames = self.calib._aslist(ndata.get('calib'))
        framelist = expandframelist(raw_frames + calib_frames)
        logger = None
        delete = output_format == pyfits.HDUList
        try:
            if (not os.access(output_dir, os.F_OK)):
                os.makedirs(output_dir)
            mkabspath(framelist, output_dir)
            logger = LogServer(logname, loglevel)
        except:
            try:
                self._cleanup(output_dir, logger, delete)
            except:
                pass
            raise
        if not threaded:
            return self._exec(output_dir, parlist, framelist, input_len, 
                              logger, output_format, delete)
        else:
            return  Threaded(
                self._exec, output_dir, parlist, framelist, input_len, 
                logger, output_format, delete)

    def _exec(self, output_dir, parlist, framelist, input_len, 
              logger, output_format, delete):
        try:
            return Result(self._recipe.frameConfig(), output_dir,
                          self._recipe.run(output_dir, parlist, framelist,
                                           logger.logfile, logger.level, self.memory_dump),
                          input_len, logger, output_format)
        finally:
            self._cleanup(output_dir, logger, delete)

    def _get_raw_frames(self, *data, **ndata):
        '''Return the input frames.

        Returns a :class:`list` with (tag, the input frame(s)) pairs. Note
        that more than one input tag is not allowed here.
        '''
        data = list(data)
        if 'raw' in ndata:
            data.append(ndata['raw'])
        tag = ndata.get('tag', self.tag)
        m = { }
        for f in data:
            if isinstance(f, dict):
                m.update(f)
            elif tag is None:
                raise ValueError('No raw input tag')
            elif tag not in m:
                m[tag] = f
            elif isinstance(m[tag], list) \
                    and not isinstance(m[tag], pyfits.HDUList):
                m[tag].append(f)
            else:
                m[tag] = [ m[tag], f ]
        return list(m.iteritems())

    def _cleanup(self, output_dir, logger, delete):
        try:
            bt = os.path.join(output_dir, 'recipe.backtrace-unprocessed')
            if os.path.exists(bt):
                with file(bt) as bt_file:
                    os.rename(bt, os.path.join(output_dir, 'recipe.backtrace'))
                    ex = RecipeCrash(bt_file)
                    ex.log(logger.logger)
                    raise ex

        finally:
            if delete:
                shutil.rmtree(output_dir)

    @property
    def __doc__(self):
        s = '%s\n\n%s\n\n' % (self.description[0], self.description[1])
        
        r = 'Parameters:\n' 
        maxlen = max(len(p.name) for p in self.param)
        for p in self.param:
            r += ' %s: %s (default: %s)\n' % (
                p.name.rjust(maxlen), p.__doc__, `p.default`)
        r += '\n'
        if self._recipe.frameConfig() is not None:
            c = 'Calibration frames: %s\n\n' % `[f.tag for f in self.calib]`
        else:
            c = ''
        if self.tags is not None:
            t = 'Raw and product frames:\n'
            maxlen = max(len(f) for f in self.tags)
            for f in self.tags:
                t += ' %s --> %s\n' % (f.rjust(maxlen), `self.output(f)`)
        else:
            t = ''
        print s + r + c + t + '\n\n'

    def __repr__(self):
        return 'Recipe(%s, version = %s)' % (`self.__name__`, `self.version[0]`)

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

