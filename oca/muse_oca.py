from optparse import OptionParser
import cpl
from ocawriter import to_oca
from cplrules import CplRules

oparser = OptionParser()
oparser.add_option('-r', '--path', help = 'MUSE recipe path',
                   default = '/tmp/musetest')
oparser.add_option('-v', '--version', help = 'Use specified MUSE version')
oparser.add_option('-o', '--outfile', help = 'OCA output file (default: stdout)')

(opt, filenames) = oparser.parse_args()

cpl.Recipe.path = opt.path
recipes = [ cpl.Recipe(name, version = opt.version) 
            for name,versions in cpl.Recipe.list() 
            if opt.version is None or opt.version in versions ]
organizer = CplRules(recipes)

if opt.outfile:
    file(opt.outfile, 'w').write(to_oca(organizer))
else:
    print to_oca(organizer)
