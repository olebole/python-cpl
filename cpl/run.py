import cpl
import sys
import logging

from optparse import OptionParser, OptionGroup

cpl.esorex.init()
    
for i in range(1, len(sys.argv)):
    if not sys.argv[i].startswith('--'):
        recipe = cpl.Recipe(sys.argv[i])
        recipe.output_dir = '.'
        del sys.argv[i]
        break
else:
    recipe = None

parser = OptionParser(prog='%s %s' % (sys.argv[0], recipe.__name__),
                      version = recipe.__version__, 
                      description=recipe.description[0],
                      epilog=recipe.description[1] + '\n') if recipe else \
         OptionParser(prog=sys.argv[0], 
                      version=cpl.__version__)
    
def output_dir_callback(option, opt, value, parser):
    recipe.output_dir = value

parser.add_option('--output-dir', action = 'callback',
                  type='str', help = 
                  'The directory where the product files will be written',
                  callback = output_dir_callback)

log = logging.getLogger()
log.setLevel(logging.INFO)
cpl.esorex.msg.level = logging.ERROR
    
def logfile_callback(option, opt, value, parser):
    ch = logging.FileHandler(value)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    log.addHandler(ch)

parser.add_option('--log-file', action = 'callback',
                  type='str', help = 'Filename of logfile',
                  callback = logfile_callback)

def loglevel_callback(option, opt, value, parser):
    levels = {'debug':logging.DEBUG, 'info':logging.INFO, 
              'warning':logging.warning, 'error':logging.ERROR }
    log.setLevel(levels[value])
    
parser.add_option('--log-level', action = 'callback',
                  type='str', help = 'Controls the severity level of '
                  'messages that will be printed to the logfile.',
                  callback = loglevel_callback)

def msglevel_callback(option, opt, value, parser):
    levels = {'debug':logging.DEBUG, 'info':logging.INFO, 
              'warning':logging.warning, 'error':logging.ERROR }
    cpl.esorex.msg.level = levels[value]

parser.add_option('--msg-level', action = 'callback',
                  type='str', help = 'Controls the severity level of '
                  'messages that will be printed to the terminal.',
                  callback = msglevel_callback)

def tag_callback(option, opt, value, parser):
    recipe.tag = value


def param_callback(option, opt, value, parser, p):
    p.value = value

def calib_callback(option, opt, value, parser, c):
    p.frame = value

types = { bool:'string', str:'string', int:'int', float:'float' }

if recipe:
    parser.add_option('--tag', action = 'callback',
                      type='str', help = 
                      'Input file tag %s' % repr(recipe.tags),
                      callback = tag_callback)

    group = OptionGroup(parser, 'Recipe parameters')
    for p in recipe.param:
        group.add_option('--%s' % p.name, action = 'callback', 
                         type=types.get(p.default.__class__),
                         help = '%s [%s]' % (p.__doc__, p.default),
                         callback = param_callback, callback_args = (p,))
    parser.add_option_group(group)

    if len(recipe.calib) > 0:
        group = OptionGroup(parser, 'Calibration frames')
            
        for f in recipe.calib:
            help = ''
            if f.min < 1:
                help = 'optional'
            elif f.min > 1:
                help = 'min %i' % f.min
            else:
                help = 'required'
            if f.max != 1:
                if help:
                    help += ', '
                help += 'may be repeated'
            group.add_option('--%s' % f.tag, action='callback', 
                             type = 'string', help = help,
                             callback = calib_callback, 
                             callback_args = (f,))
        parser.add_option_group(group)

(option, args) = parser.parse_args(sys.argv)

if not args[1:]:
    parser.print_help()
    sys.exit()
    
try: 
    recipe(args[1:])
except cpl.result.RecipeCrash as ex:
    log.exception(ex)
    print(repr(ex))
except cpl.result.CplError as ex:
    log.exception(ex)
    print(repr(ex))
    
    
