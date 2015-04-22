'''Python interface for the Common Pipeline Library

This module can list, configure and execute CPL-based recipes from Python
(python2 and python3).  The input, calibration and output data can be
specified as FITS files or as ``astropy.io.fits`` objects in memory.

The ESO `Common Pipeline Library <http://www.eso.org/sci/software/cpl/>`_
(CPL) comprises a set of ISO-C libraries that provide a comprehensive,
efficient and robust software toolkit. It forms a basis for the creation of
automated astronomical data-reduction tasks. One of the features provided by
the CPL is the ability to create data-reduction algorithms that run as plugins
(dynamic libraries). These are called "recipes" and are one of the main
aspects of the CPL data-reduction development environment.
'''

from __future__ import absolute_import

from .version import version as __version__
from .version import author as __author__
from .version import email as __email__
from .version import license_ as __license__

from .recipe import Recipe
from .param import Parameter
from .frames import FrameConfig
from .result import Result, CplError, RecipeCrash
from . import dfs
from . import esorex
from . import CPL_recipe

Recipe.dir = '.'
cpl_versions = [ '%i.%i.%i' % ver for ver in CPL_recipe.cpl_versions() ]
del CPL_recipe
del absolute_import
del recipe, version, param, frames, result, md5sum
try:
    del ver
except NameError:
    pass
