from version import __version__
import os
import sys

from recipes import Recipe
from parameters import Parameter
from frames import FrameConfig, Result, CplError
from log import msg

msg.domain = os.path.basename(sys.argv[0])
msg.level = msg.OFF

Recipe.dir = '/work1/oles/Projects/2009/Muse/Pipeline/lib/muse/'
