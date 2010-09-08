import os
import tempfile

import CPL_recipe
import esorex
import threading
from frames import RestrictedFrameList, UnrestrictedFrameList, Result, mkabspath
from parameters import ParameterList
from log import msg

class Recipe(object):
    '''Pluggable Data Reduction Module (PDRM) from a ESO pipeline. 

    Recipes are loaded from shared libraries that are provided with the
    pipeline library of the instrument.

    The libraries are searched in the directories specified by the class
    attribute :attr:`Recipe.path` or its subdirectories. The search path is automatically
    set to the esorex path when

    >>> cpl.esorex.init()

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

    def __init__(self, name, filename = None, version = None, 
                 force_list = False, threaded = False):
        '''Try to load a recipe with the specified name in the directory
        specified by the class attribute :attr:`Recipe.path` or its subdirectories.

        :param name: Name of the recipe. Required. Use
            :func:`cpl.Recipe.list()` to get a list of available recipes.
        :type name: :class:`str`

        :param filename:   Name of the shared library. Optional. If not set, 
            :attr:`Recipe.path` is searched for the library file. 
        :type filename: :class:`str`
        :param version: Version number. Optional. If not set, the newest version is loaded.
        :type version: :class:`int` or :class:`str`
        :param force_list: Force the result to contain lists of frames even if they contain 
            only one result frame. Default is :attr:`False`. This may be also set as an 
            attribute  or specified as a parameter when calling the recipe.
        :type force_list: :class:`bool`
        :param threaded: Run the recipe in the background, returning immediately after 
            calling it. Default is :attr:`False`. This may be also set as an attribute or 
            specified as a parameter when calling the recipe. 
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
        self._calib = RestrictedFrameList(self)
        self.tag = self.tags[0]
        self.output_dir = None
        self.temp_dir = '.'
        self.force_list = force_list
        self.threaded = threaded

    def reload(self):
        '''Reload the recipe. 

        All recipe settings remain unchanged.
        '''
        self._recipe = CPL_recipe.recipe(self.filename, self.name)

    author = property(lambda self: self._recipe.author(), 
                      doc = 'Pair (author name, author email address) of two strings.')
    description = property(lambda self: self._recipe.description(),
                           doc = 'Pair (synopsis, description) of two strings.')
    version = property(lambda self: self._recipe.version(),
                       doc = 'Pair (versionnumber, versionstring) of an integer and a string. '
                       'The integer will be increased on development progress.')
    tags = property(lambda self: 
                    [ c[0][0] for c in self._recipe.frameConfig() ],
                    doc = 'Possible tags for the raw input frames, or :attr:`None` '
                    'if this information is not provided by the recipe.')

    def _set_tag(self, tag):
        if self.tags is None or tag in self.tags:
            self._tag = tag 
        else:
            raise KeyError("Tag '%s' not in %s" % (tag, str(self.tags)))

    tag = property(lambda self: self._tag, _set_tag, 
                   doc='''Default raw input frame tag. After creation, 
        it is set to the first tag from the "tags" property and may be changed 
        to any of these tags. If the recipe does not provide the tag information, 
        it must be set manually, or the tag name has to be provided when calling 
        the recipe.''')

    def _load_calib(self, source = None):
        if isinstance(source, (str, file)):
            source = esorex.load_sof(source)
        self._calib = RestrictedFrameList(self, source) 

    calib = property(lambda self: self._calib, _load_calib, _load_calib, 
                     doc = '''This attribute contains the calibration frames
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

     Using a HDU list is useful when it needs to be patched before fed into
     the recipe. Note that HDU lists are stored in temporary files before the
     recipe is called which may produce some overhead. Also, the CPL then
     assigns the temporary file names to the 

     >>> master_bias = pyfits.open('master_bias_0.fits')
     >>> master_bias[0].header['HIERARCH ESO DET CHIP1 OUT1 GAIN'] = 2.5
     >>> muse_scibasic.calib.MASTER_BIAS = 'master_bias_0.fits'

     To assign more than one frame, put them into a list:

     >>> muse_scibasic.calib.BADPIX_TABLE = [ 'badpix_1.fits', 'badpix_2.fits' ]
     
     All calibration frames can be set in one step by assigning a :class:`map` to the
     parameters. In this case, frame that are not in the map are set are removed from the 
     list, and unknown frame tags are silently ignored. The key of the map is the tag name; 
     the values are either a string, or a list of strings, containing the file name(s) or 
     the :class:`pyfits.HDUList` objects.

     >>> muse_scibasic.calib = { 'MASTER_BIAS':'master_bias_0.fits', 
     ...                         'BADPIX_TABLE':[ 'badpix_1.fits', 'badpix_2.fits' ] }

     ''')

    def _load_param(self, source = None):
        if isinstance(source, (str, file)):
            source = esorex.load_rc(source)
        self._param = ParameterList(self, source)

    param = property(lambda self: self._param, _load_param, _load_param, 
                     doc = '''This attribute contains all recipe parameters. 
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
     resample None False
     dlambda None 1.25

     On interactive sessions, all parameter settings can be easily printed by
     printing the :attr:`param` attribute of the recipe:

     >>> print muse_scibasic.param
      [Parameter('nifu', default=99), Parameter('cr', default=dcr), 
       Parameter('xbox', default=15), Parameter('ybox', default=40), 
       Parameter('passes', default=2), Parameter('thres', default=4.5), 
       Parameter('resample', default=False), Parameter('dlambda', default=1.25)]

     To set the value of a recipe parameter, the value can be assigned to the
     according attribute:

     >>> muse_scibasic.param.nifu = 1

     The new value is checked against parameter type, and possible value
     limitations provided by the recipe. In a recipe call, the same parameter can
     be specified as

     >>> res = muse_scibasic( ..., nifu = 1)

     To reset a value to its default, it is eighter deleted, or set to :attr:`None`. The
     following two lines:

     >>> muse_scibasic.param.nifu = None
     >>> del muse_scibasic.param.nifu

     will both reset the parameter to its default value. 

     All parameters can be set in one step by assigning a :class:`map` to the
     parameters. In this case, all values that are not in the map are reset to
     default, and unknown parameter names are ignored. The keys of the map may
     contain contain the name or the fullname with context:

     >>> muse_scibasic.param = { 'nifu':1, 'xbox':11, 'resample':True }

     ''')

    def output(self, tag = None):
        '''Return the list of output frame tags.

        If the recipe does not provide this information, an exception is raised.
        
        :param tag: Input (raw) frame tag. Defaults to the :attr:`Recipe.tar` attribute if 
            not specified. 
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
        :param tag = data: Data with a specific tag.
        :type data: :class:`pyfits.HDUlist` or :class:`str` or a :class:`list` of them.
        :param force_list: overwrite the :attr:`force_list` attribute (optional).
        :type force_list: :class:`bool`
        :param threaded: overwrite the :attr:`threaded` attribute (optional).
        :type threaded: :class:`bool`
        :param CPL parameter name = value: overwrite the according CPL parameter of the recipe 
                                   (optional). 
        :param Calibration tag name = value: overwrite the calibration frame list for this tag 
                                     (optional).
        :return: The object with the return frames as :class:`pyfits.HDUList` objects
        :rtype: :class:`cpl.Result`
        :raise:  IOError If the temporary directory could not be built or the files could not be 
                read/written.
        :raise:  CPLError If the recipe returns an error or crashed.

        .. note:: If the recipe is executed in the background (``threaded = True``) and an exception occurs,
             this exception is raised whenever result fields are accessed.
        '''
        recipe_dir = self.output_dir if self.output_dir \
            else tempfile.mkdtemp(dir = self.temp_dir, 
                                  prefix = self.name + "-") if self.temp_dir \
            else os.getcwd()
        parlist = self.param._aslist(**ndata)
        framelist = self.calib._aslist(*data, **ndata)
        force_list = ndata.get('force_list', self.force_list)
        threaded = ndata.get('threaded', self.threaded)
        tmpfiles = list()
        try:
            if (not os.access(recipe_dir, os.F_OK)):
                os.makedirs(recipe_dir)
            tmpfiles = mkabspath(framelist, recipe_dir)
            msg.info("Executing %s (version %s, CPL version %s)" 
                     % (self.name, self.version[1], CPL_recipe.version()))
            msg.indent_more()
            if parlist:
                msg.info("parameters:")
                msg.indent_more()
                for name, value in parlist:
                    msg.info("%s = %s" % (name, str(value)))
                msg.indent_less()
            if framelist:
                msg.info("frames:")
                msg.indent_more()
                for tag, file in framelist:
                    msg.info("%s = %s" % (tag, file))
                msg.indent_less()
                msg.indent_less()
        except:
            self._cleanup(recipe_dir, tmpfiles)
            raise

        return self._exec(recipe_dir, parlist, framelist, force_list, tmpfiles) \
            if not threaded else \
            Threaded(self._exec, recipe_dir, parlist, framelist, force_list, tmpfiles)

    def _exec(self, recipe_dir, parlist, framelist, force_list, tmpfiles):
        try:
            r = Result(self._recipe.frameConfig(), recipe_dir,
                       self._recipe.run(recipe_dir, parlist, framelist),
                       (self.temp_dir and not self.output_dir),
                       force_list)
            return r
        finally:
            self._cleanup(recipe_dir, tmpfiles)

    def _cleanup(self, recipe_dir, tmpfiles):
            for f in tmpfiles:
                os.remove(f)
            if self.temp_dir and not self.output_dir:
                try:
                    os.rmdir(recipe_dir)
                except:
                    pass

    __doc__ = property(lambda self: 
                       self.description[0] + '\n\n' + self.description[1])

    def __repr__(self):
        return "Recipe('%s')" % self.name

    def list():
        '''Return a list of recipes.
        
        Searches for all recipes in in the directory specified by the class
        attribute :attr:`Recipe.path` or its subdirectories. 
        '''
        plugins = { }
        for f in Recipe.get_libs():
            plugin_f = CPL_recipe.list(f)
            if plugin_f:
                for p in plugin_f:
                    plugins.setdefault(p[0], list()).append(p[2])
        return list(plugins.items())
    list = staticmethod(list)

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
    get_recipefilename = staticmethod(get_recipefilename)

    def get_libs():
        libs = [ ]
        path = Recipe.path.split(':') if isinstance(Recipe.path, str) else Recipe.path
        for p in path:
            for root, dir, files in os.walk(p):
                libs += [ os.path.join(root, f) 
                           for f in files if f.endswith('.so') ]
        return libs
    get_libs = staticmethod(get_libs)


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
    def __init__(self, func, *args, **nargs):
        threading.Thread.__init__(self)
        self._func = func
        self._args = args
        self._nargs = nargs
        self._res = None
        self._exception = None
        self.start()
        
    def run(self):
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
