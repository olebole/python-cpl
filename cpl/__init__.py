import os
import sys

from version import version as __version__
from version import author as __author__
from version import email as __email__
from version import license_ as __license__
from version import doc as __doc__

from recipe import Recipe
from param import Parameter
from frames import FrameConfig
from result import Result, CplError, RecipeCrash
import dfs
import esorex

Recipe.dir = '.'
cpl_versions = [ '%i.%i.%i' % ver for ver in CPL_recipe.cpl_versions() ]
