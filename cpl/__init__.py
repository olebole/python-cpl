from version import __version__

from recipes import Recipe, RecipeCrash
from parameters import Parameter
from frames import FrameConfig, Result, CplError
from log import msg, lib_version

Recipe.dir = '.'
