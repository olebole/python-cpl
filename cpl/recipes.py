import os
import tempfile

import CPL_recipe
import esorex
import threading
from frames import RestrictedFrameList, UnrestrictedFrameList, Result, mkabspath
from parameters import ParameterList
from log import msg

class Recipe(object):
    '''Attributes:
    
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
        specified by the module variable 'recipe_dir' or its subdirectories.
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
        '''
        self._recipe = CPL_recipe.recipe(self.filename, self.name)

    author = property(lambda self: self._recipe.author(), 
                      doc = '(author, email) pair')
    description = property(lambda self: self._recipe.description(),
                           doc = '(synopsis, description) pair')
    version = property(lambda self: self._recipe.version(),
                       doc = '(versionnumber, versionstring) pair')
    tags = property(lambda self: 
                    [ c[0][0] for c in self._recipe.frameConfig() ])

    def _set_tag(self, tag):
        if tag in self.tags:
            self._tag = tag 
        else:
            raise KeyError("Tag '%s' not in %s" % (tag, str(self.tags)))

    tag = property(lambda self: self._tag, _set_tag)

    def _load_calib(self, source = None):
        if isinstance(source, (str, file)):
            source = esorex.load_sof(source)
        self._calib = RestrictedFrameList(self, source) 

    calib = property(lambda self: self._calib, _load_calib, _load_calib)

    def _load_param(self, source = None):
        if isinstance(source, (str, file)):
            source = esorex.load_rc(source)
        self._param = ParameterList(self, source)

    param = property(lambda self: self._param, _load_param, _load_param)

    def output(self, tag = None):
        if tag is None:
            tag = self.tag
        for c in self._recipe.frameConfig():
            if tag == c[0][0]:
                return c[2]

    def __call__(self, *data, **ndata):
        '''Call the recipes execution with a certain input frame.
        
        Parameters
        data:       Data input frames, using the default tag.
        tag = data: Data with a specific tag.
              
        data may be a single HDUlist, a single file name, or a list of them.

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
            Thread(self, recipe_dir, parlist, framelist, force_list, tmpfiles)

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
        
        Searches for all recipes in in the directory specified by the module
        variable 'recipe_dir' or its subdirectories.
        '''
        plugins = list()
        for f in Recipe.get_libs():
            plugin_f = CPL_recipe.list(f)
            if plugin_f:
                plugins += [ p[0] for p in plugin_f ] 
        return plugins
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


class Thread(threading.Thread):
    '''Threading interface. 

    '''
    def __init__(self, recipe, *args):
        threading.Thread.__init__(self)
        self._recipe = recipe
        self._args = args
        self._res = None
        self._exception = None
        self.start()
        
    def run(self):
        try:
            self._res = self._recipe._exec(*self._args)
        except Exception as exception:
            self._exception = exception

    def __getattr__(self, name):
        self.join()
        if self._exception is None:
            return self._res.__dict__[name]
        else:
            raise self._exception
