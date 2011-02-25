import sys
import parser

from ocawriter import to_oca
from organizer import OcaOrganizer
from pyparser import parseFile


organizer = OcaOrganizer(parseFile(sys.argv[1]))
print to_oca(organizer)
