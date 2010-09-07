__version__ = '0.1.0'

import os
import sys

from recipes import Recipe
from parameters import Parameter
from frames import FrameConfig, Result
from log import msg

msg.domain = os.path.basename(sys.argv[0])

Recipe.dir = '/work1/oles/Projects/2009/Muse/Pipeline/lib/muse/'
