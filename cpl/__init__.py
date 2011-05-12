from version import __version__
import os
import sys

from recipes import Recipe, RecipeCrash
from parameters import Parameter
from frames import FrameConfig, Result, CplError
from log import msg, lib_version

msg.domain = os.path.basename(sys.argv[0])
msg.level = msg.OFF

Recipe.dir = '.'
