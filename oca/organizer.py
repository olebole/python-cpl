import sys
from optparse import OptionParser
import fnmatch

import numpy
import pyfits

class Constant(object):
    def __init__(self, value):
        self.value = value
        self.name = '"%s"' % value if isinstance(value, (str, unicode)) \
            else str(value)
        self.keywords = set()
        
    def __call__(self, var):
        return self.value

class FitsKeyword(object):
    def __init__(self, name):
        self.name = name
        
    def __call__(self, var):
        return var.get(self.name)

    @property
    def keywords(self):
        return set((self.name,))

def likeFunc(template, s):
    if s is None:
        return False
    for esc in '*.[]\\':
        template = template.replace(esc, '\\' + esc)
        template = template.replace('%', '*')
    return fnmatch.fnmatch(template, s)

class Expression(object):
    ops = { 
        'and': lambda param, var: numpy.all(param),
        'or': lambda param, var: numpy.any(param),
        '==': lambda param, var: param[0] is not None \
        and param[1] is not None and param[0] == param[1],
        'is': lambda param, var: param[0] is param[1],
        'like': lambda param, var: likeFunc(param[1], param[0]),
        '?=': lambda param, var: param[0] is None or param[1] is None \
            or param[0] == param[1],
        '!=': lambda param, var: param[0] != param[1],
        '<': lambda param, var: param[0] < param[1],
        '<=': lambda param, var: param[0] <= param[1],
        '>': lambda param, var: param[0] > param[1],
        '>=': lambda param, var: param[0] >= param[1],
        '+': lambda param, var: sum(param),
        '-': lambda param, var: param[0] - param[1],
        '*': lambda param, var: param[0] * param[1],
        '/': lambda param, var: param[0] / param[1],
        '%': lambda param, var: param[0] % param[1],
        }

    def __init__(self, op, pars):
        self.op = Expression.ops[op]
        self.name = op
        self.pars = pars

    def __call__(self, var):
        return self.op([p(var) for p in self.pars], var) 

    @property
    def keywords(self):
        return set().union(*(p.keywords for p in self.pars))

class Assignment(object):
    def __init__(self, target, expression):
        self.target = target
        self.expression = expression

    def __call__(self, var = None):
        var[self.target] = self.expression(var)

    @property
    def keywords(self):
        return self.expression.keywords

    @property
    def targets(self):
        return set((self.target, ))

class ClassificationRule(object):
    def __init__(self, condition, assignments):
        self.condition = condition
        self.assignments = assignments

    def __call__(self, var):
        if self.condition(var):
            for a in self.assignments:
                a(var)

    @property
    def keywords(self):
        return set(self.condition.keywords). \
            union(*(a.keywords for a in self.assignments))
        
    @property
    def targets(self):
        return set().union(*(a.targets for a in self.assignments))

class OrganizationRule(object):
    def __init__(self, actionname, dataset, condition, grouping, alias):
        self.actionname = actionname
        self.condition = condition
        self.dataset = dataset
        self.grouping = grouping
        self.alias = alias

    def __call__(self, var):
        ret = dict()
        for v in var:
            if self.condition(v):
                g = tuple(v.get(s) for s in self.grouping)
                ret.setdefault(g, list()).append(v)
        return ret.values()

    @property
    def keywords(self):
        return self.condition.keywords

class AssociationRule(object):
    def __init__(self, name, datasource, condition, cardinality):
        self.name = name
        self.datasource = datasource
        self.condition = condition
        self.cardinality = cardinality

    def __call__(self, var, inputfile = {}):
        return [ v for v in var if self.condition(dict(
                    [(key,value) for key, value in v.iteritems()]
                    + [('inputfile.' + key,value) 
                       for key, value in inputfile.iteritems()])) ]

    @property
    def keywords(self):
        return set(k.replace('inputFile.', '') for k in self.condition.keywords)

class ProductDef(object):
    def __init__(self, name, assignments):
        self.name = name
        self.assignments = assignments

    def __call__(self, var = None):
        var = dict(var) if var else dict()
        for a in  self.assignments:
            a(var)
        return var

    @property
    def keywords(self):
        return set().union(*(a.keywords for a in self.assignments))
        
    @property
    def targets(self):
        return set().union(*(a.targets for a in self.assignments))

class RecipeDef(object):
    def __init__(self, name, param):
        self.name = name
        self.param = param

class ActionRule(object):
    def __init__(self, name, associations, recipedef, products):
        self.name = name
        self.associations = associations
        self.recipedef = recipedef
        self.products = products 

    def calib(self, var, inputfile = {}):
        ret = dict()
        for r in self.associations:
            for v in r(var, inputfile):
                ret.setdefault(r.name, list()).append(v)
        return ret

    @property
    def keywords(self):
        return set().union(*(a.keywords for a in self.associations)). \
            union(*(p.keywords for p in self.products))
        
    @property
    def targets(self):
        return set().union(*(p.targets for p in self.products))

class OcaOrganizer(object):
    def __init__(self, classifications, groups, action):
        self.classifications = classifications
        self.groups = groups
        self.action = dict((a.name, a) for a in action)

    def classify(self, var):
        for c in self.classifications:
            c(var)

    def group(self, var):
        ret = dict()
        for r in self.groups:
            for v in r(var):
                ret.setdefault(r.actionname, list()).append(v)
        return ret

    @property
    def keywords(self):
        return  set().union(*(c.keywords for c in self.classifications)). \
            union(*(g.keywords for g in self.groups)). \
            union(*(a.keywords for a in self.action.values()))
        
    @property
    def targets(self):
        return set().union(*(c.keywords for c in self.classifications)). \
            union(*(a.targets for a in self.action.values()))

# ------------------------------------------------------------------------

if __name__ == "__main__":
    import pyparser

    oparser = OptionParser(usage='%prog files')
    oparser.add_option('-r', '--rules', help = 'OCA rules file')

    (opt, filenames) = oparser.parse_args()
    if not opt.rules:
        oparser.print_help()
        sys.exit()

    organizer = pyparser.parseFile(opt.rules)
    print 'keywords', organizer.keywords
    print 'categories', organizer.targets

    files = list()
    for f in filenames:
        hdulist = pyfits.open(f)
        var = dict(hdulist[0].header)
        var.setdefault('FILENAME', f)
        organizer.classify(var)
        files.append(var)

    for var in [
        {'OBJECT':'BIAS', 'FILENAME':'bias.fits'},
        {'OBJECT':'BIAS', 'FILENAME':'bias2.fits'},
        {'OBJECT':'FLAT', 'FILENAME':'flat.fits'},
        {'OBJECT':'FLAT', 'FILENAME':'flat2.fits'},
        {'OBJECT':'FLAT', 'FILENAME':'flat3.fits'},
        {'OBJECT':'DARK', 'FILENAME':'dark.fits'},
        {'OBJECT':'DARK', 'FILENAME':'dark2.fits'},
        {'OBJECT':'DARK', 'FILENAME':'dark3.fits'},
        {'OBJECT':'SKY', 'FILENAME':'sky.fits'},
        {'DPR.TYPE':'BADPIX_TABLE', 'FILENAME':'bpixtable.fits'},
        ]:
        organizer.classify(var)
        files.append(var)

    for name, f in organizer.group(files).iteritems():
        for i, fn in enumerate(f):
            c = list()
            for ca in [ cc[1] for cc in 
                        organizer.action[name].calib(files, fn[0]).items()]:
                c += ca
            print '%s-%i.zip' % (name, i+1), [n.get('FILENAME') 
                                              for n in (fn + c) ]

