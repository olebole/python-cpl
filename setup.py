from distutils.core import setup, Extension

module1 = Extension('cpl.CPL_recipe',
                    libraries = [ 'cplcore', 'cpldfs', 'cplui', 'cpldrs', 'gomp' ],
                    sources = ['cpl/CPL_recipe.c'])

setup (name = 'cpl',
       version = '0.0.0',
       author = 'Ole Streicher',
       author_email = 'ole@aip.de',
       description = 'Python interface for the Common Pipeline Library',
       packages = [ 'cpl'],
       ext_modules = [module1])

