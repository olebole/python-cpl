import organizer

def Expression(obj):
    if obj.op == organizer.fitskeyword:
        return obj.pars[0]([])
    elif len(obj.pars) == 0:
        return obj.name
    else:
        if obj.pars[0].op in (obj.op, organizer.fitskeyword) or not obj.pars[0].pars:
            s = Expression(obj.pars[0])
        else:
            s = '(%s)' % Expression(obj.pars[0])
        for p in obj.pars[1:]:
            if p.op in (obj.op, organizer.fitskeyword) or not p.pars:
                s = '%s %s %s' % (s, obj.name, Expression(p))
            else:
                s = '%s %s (%s)' % (s, obj.name, Expression(p))
        return '%s' % s

def Assignment(obj):
    return '%s = %s;' % (obj.target, Expression(obj.expression))

def ClassificationRule(obj):
    s = 'if %s then {\n' % Expression(obj.condition)
    for a in obj.assignments:
        s += '  %s\n' % Assignment(a)
    s += '}\n'
    return s

def Classificator(obj):
    s = ''
    for c in obj.rules:
        s += ClassificationRule(c)
    return s
    
def OrganizationRule(obj):
    s = 'select execute(%s) from %s where %s' % (obj.actionname, obj.dataset, 
                                                 Expression(obj.condition))
    if obj.grouping:
        s += ' group by %s' % obj.grouping[0]
        for g in obj.grouping[1:]:
            s += ', %s' % g
    if obj.alias:
        s += ' as (%s' % obj.alias[0]
        for g in obj.alias[1:]:
            s += ', %s' % g
        s += ')'
    return s + ';\n'

def Organizator(obj):
    s = ''
    for c in obj.rules:
        s += OrganizationRule(c)
    return s

def AssociationRule(obj):
    s = ''
    if obj.cardinality[0] != 1:
        s += 'minRet = %i; ' % obj.cardinality[0]
    if obj.cardinality[1] != 1:
        s += 'maxRet = %i; ' % obj.cardinality[1]
    s += 'select file as %s from %s where %s;' % (obj.name, obj.datasource, 
                                                  Expression(obj.condition))
    return s

def ProductDef(obj):
    s = 'product %s' % obj.name
    if obj.assignments:
        s +=' {'
        for a in obj.assignments:
            s += ' %s' % Assignment(a)
        s +=' }'
    else:
        s +=';'
    return s

def RecipeDef(obj):
    s = 'recipe %s' % obj.name
    if obj.param:
        s += ' {'
        for p, v in obj.param.items():
            s += ' "--%s=%s";' % (p,v) 
        s += ' }'
    else:
        s +=';'
    return s

def ActionRule(obj):
    s = 'action %s {\n' % obj.name
    for a in obj.associations:
        s += '  %s\n' % AssociationRule(a)
    if obj.recipedef:
        s += '  %s\n' % RecipeDef(obj.recipedef)
    for p in obj.products:
        s += '  %s\n' % ProductDef(p)
    s += '}\n'
    return s

def OcaOrganizer(obj):
    s = Classificator(obj.classify) + Organizator(obj.group)
    for a in obj.action.values():
        s += ActionRule(a)
    return s
