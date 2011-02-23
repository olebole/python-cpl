import sys
from optparse import OptionParser
import fnmatch

import numpy
import pyfits

def likeFunc(template, s):
    if s is None:
        return False
    for esc in '*.[]\\':
        template = template.replace(esc, '\\' + esc)
        template = template.replace('%', '*')
    return fnmatch.fnmatch(template, s)

def fitskeyword(param, var):
    return var.get(param[0])

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
        'FitsKeyword': fitskeyword,
        }

    def __init__(self, expr):
        try:
            self.op = Expression.ops[expr.op]
            self.pars = [ Expression(p) for p in expr.param ]
            self.name = expr.op
        except AttributeError:
            self.op = lambda param, var: expr
            self.pars = [ ]
            self.name = '"%s"' % expr if isinstance(expr, (str, unicode)) \
                else str(expr)

    def __call__(self, var):
        return self.op([p(var) for p in self.pars], var) 

    @property
    def keywords(self):
        if self.op == fitskeyword:
            return set([self.pars[0]([])])
        else:
            s = set()
            for p in self.pars:
                s = s.union(p.keywords)
            return s

    @property
    def oca(self):
        if self.op == fitskeyword:
            return self.pars[0]([])
        elif len(self.pars) == 0:
            return self.name
        else:
            if self.pars[0].op in (self.op, fitskeyword) or not self.pars[0].pars:
                s = self.pars[0].oca
            else:
                s = '(%s)' % self.pars[0].oca
            for p in self.pars[1:]:
                if p.op in (self.op, fitskeyword) or not p.pars:
                    s = '%s %s %s' % (s, self.name, p.oca)
                else:
                    s = '%s %s (%s)' % (s, self.name, p.oca)
            return '%s' % s

class Assignment(object):
    def __init__(self, ass):
        self.target = ass.target
        self.expression = Expression(ass.expression)

    def __call__(self, var = None):
        var[self.target] = self.expression(var)

    @property
    def keywords(self):
        return self.expression.keywords

    @property
    def targets(self):
        return set((self.target, ))

    @property
    def oca(self):
        return '%s = %s;' % (self.target, self.expression.oca)

class ClassificationRule(object):
    def __init__(self, rule):
        self.condition = Expression(rule.condition)
        self.assignments = [ Assignment(a) for a in rule.assignments ]

    def __call__(self, var):
        if self.condition(var):
            for a in self.assignments:
                a(var)

    @property
    def keywords(self):
        s = set(self.condition.keywords)
        for a in self.assignments:
            s = s.union(a.keywords)
        return s
        
    @property
    def targets(self):
        s = set()
        for a in self.assignments:
            s = s.union(a.targets)
        return s

    @property
    def oca(self):
        s = 'if %s then {\n' % self.condition.oca
        for a in self.assignments:
            s += '  %s\n' % a.oca
        s += '}\n'
        return s

class Classificator(object):
    def __init__(self, rules):
        self.rules = [ ClassificationRule(r) for r in rules ]

    def __call__(self, var):
        for r in self.rules:
            r(var)

    @property
    def keywords(self):
        s = set()
        for r in self.rules:
            s = s.union(r.keywords)
        return s

    @property
    def targets(self):
        s = set()
        for r in self.rules:
            s = s.union(r.targets)
        return s

    @property
    def oca(self):
        s = ''
        for c in self.rules:
            s += c.oca
        return s
    
class OrganizationRule(object):
    def __init__(self, rule):
        self.actionname = rule.actionname
        self.condition = Expression(rule.condition)
        self.dataset = rule.dataset
        self.grouping = rule.grouping
        self.alias = rule.alias

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

    @property
    def oca(self):
        s = 'select execute(%s) from %s where %s' % (self.actionname, self.dataset, self.condition.oca)
        if self.grouping:
            s += ' group by %s' % self.grouping[0]
            for g in self.grouping[1:]:
                s += ', %s' % g
        if self.alias:
            s += ' as (%s' % self.alias[0]
            for g in self.alias[1:]:
                s += ', %s' % g
            s += ')'
        return s + ';\n'
        

class Organizator(object):
    def __init__(self, rules):
        self.rules = [OrganizationRule(r) for r in rules]

    def __call__(self, var):
        ret = dict()
        for r in self.rules:
            for v in r(var):
                ret.setdefault(r.actionname, list()).append(v)
        return ret

    @property
    def keywords(self):
        s = set()
        for r in self.rules:
            s = s.union(r.keywords)
        return s

    @property
    def oca(self):
        s = ''
        for c in self.rules:
            s += c.oca
        return s

class AssociationRule(object):
    def __init__(self, rule):
        self.name = rule.name
        self.datasource = rule.datasource
        self.condition = Expression(rule.condition)
        self.cardinality = rule.cardinality

    def __call__(self, var, inputfile = {}):
        return [ v for v in var if self.condition(dict(
                    [(key,value) for key, value in v.iteritems()]
                    + [('inputfile.' + key,value) 
                       for key, value in inputfile.iteritems()])) ]

    @property
    def keywords(self):
        return set([ k.replace('inputFile.', '') 
                     for k in self.condition.keywords] )

    @property
    def oca(self):
        s = ''
        if self.cardinality[0] != 1:
            s += 'minRet = %i; ' % self.cardinality[0]
        if self.cardinality[1] != 1:
            s += 'maxRet = %i; ' % self.cardinality[1]
        s += 'select file as %s from %s where %s;' % (self.name, self.datasource, self.condition.oca)
        return s

class ProductDef(object):
    def __init__(self, product):
        self.name = product.name
        self.assignments = [ Assignment(a) for a in product.assignments ]

    def __call__(self, var = None):
        var = dict(var) if var else dict()
        for a in  self.assignments:
            a(var)
        return var

    @property
    def keywords(self):
        s = set()
        for a in self.assignments:
            s = s.union(a.keywords)
        return s
        
    @property
    def targets(self):
        s = set()
        for a in self.assignments:
            s = s.union(a.targets)
        return s

    @property
    def oca(self):
        s = 'product %s' % self.name
        if self.assignments:
            s +=' {'
            for a in self.assignments:
                s += ' %s' % a.oca
            s +=' }'
        else:
            s +=';'
        return s

class RecipeDef(object):
    def __init__(self, recipe):
        self.name = recipe.name
        self.param = recipe.parameters

    @property
    def oca(self):
        s = 'recipe %s' % self.name
        if self.param:
            s += ' {'
            for p, v in self.param.items():
                s += ' "--%s=%s";' % (p,v) 
            s += ' }'
        else:
            s +=';'
        return s

class ActionRule(object):
    def __init__(self, rule):
        self.name = rule.name
        self.associations = [ AssociationRule(a) 
                              for a in rule.associations ]
        self.recipedef = RecipeDef(rule.recipe) if rule.recipe else None
        self.products = [ ProductDef(p) for p in rule.products ]

    def calib(self, var, inputfile = {}):
        ret = dict()
        for r in self.associations:
            for v in r(var, inputfile):
                ret.setdefault(r.name, list()).append(v)
        return ret

    @property
    def keywords(self):
        s = set()
        for a in self.associations + self.products:
            s = s.union(a.keywords)
        return s
        
    @property
    def targets(self):
        s = set()
        for a in self.products:
            s = s.union(a.targets)
        return s

    @property
    def oca(self):
        s = 'action %s {\n' % self.name
        for a in self.associations:
            s += '  %s\n' % a.oca
        if self.recipedef:
            s += '  %s\n' % self.recipedef.oca
        for p in self.products:
            s += '  %s\n' % p.oca
        s += '}\n'
        return s

class OcaOrganizer(object):
    def __init__(self, rules):
        self.classify = Classificator(rules.classification)
        self.group = Organizator(rules.grouping)
        self.action = dict((a.name, ActionRule(a)) for a in rules.actions)

    @property
    def keywords(self):
        s = set(self.classify.keywords).union(self.group.keywords)
        for a in self.action.values():
            s = s.union(a.keywords)
        return s
        
    @property
    def targets(self):
        s = set(self.classify.targets)
        for a in self.action.values():
            s = s.union(a.targets)
        return s

    @property
    def oca(self):
        s = self.classify.oca + self.group.oca
        for a in self.action.values():
            s += a.oca
        return s
# ------------------------------------------------------------------------

if __name__ == "__main__":

    import pyparser as parser

    oparser = OptionParser(usage='%prog files')
    oparser.add_option('-r', '--rules', help = 'OCA rules file')

    (opt, filenames) = oparser.parse_args()
    if not opt.rules:
        oparser.print_help()
        sys.exit()

    organizer = OcaOrganizer(parser.parseFile(opt.rules))
    print 'keywords', organizer.keywords
    print 'categories', organizer.targets
    print organizer.oca

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

