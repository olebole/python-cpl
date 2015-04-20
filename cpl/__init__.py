from __future__ import absolute_import

from .version import version as __version__
from .version import author as __author__
from .version import email as __email__
from .version import license_ as __license__
from .version import doc as __doc__

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
