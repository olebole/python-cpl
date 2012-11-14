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
from logger import msg,log
import dfs
import esorex

Recipe.dir = '.'
