from __future__ import absolute_import
import os
import sys

from cpl.version import version as __version__
from cpl.version import author as __author__
from cpl.version import email as __email__
from cpl.version import license_ as __license__
from cpl.version import doc as __doc__

from cpl.recipe import Recipe
from cpl.param import Parameter
from cpl.frames import FrameConfig
from cpl.result import Result, CplError, RecipeCrash
from . import dfs
from . import esorex
from . import CPL_recipe

Recipe.dir = '.'
cpl_versions = [ '%i.%i.%i' % ver for ver in CPL_recipe.cpl_versions() ]
