import organizer

def from_expression(obj):
    if obj.op == organizer.fitskeyword:
        return obj.pars[0]([])
    elif len(obj.pars) == 0:
        return obj.name
    else:
        if obj.pars[0].op in (obj.op, organizer.fitskeyword) or not obj.pars[0].pars:
            s = from_expression(obj.pars[0])
        else:
            s = '(%s)' % from_expression(obj.pars[0])
        for p in obj.pars[1:]:
            if p.op in (obj.op, organizer.fitskeyword) or not p.pars:
                s = '%s %s %s' % (s, obj.name, from_expression(p))
            else:
                s = '%s %s (%s)' % (s, obj.name, from_expression(p))
        return '%s' % s

def from_assignment(obj):
    return '%s = %s;' % (obj.target, from_expression(obj.expression))

def from_classificationrule(obj):
    s = 'if %s then {\n' % from_expression(obj.condition)
    for a in obj.assignments:
        s += '  %s\n' % from_assignment(a)
    s += '}\n'
    return s

def from_classificator(obj):
    s = ''
    for c in obj.rules:
        s += from_classificationrule(c)
    return s
    
def from_organizationrule(obj):
    s = 'select execute(%s) from %s where %s' % (obj.actionname, obj.dataset, 
                                                 from_expression(obj.condition))
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

def from_organizator(obj):
    s = ''
    for c in obj.rules:
        s += from_organizationrule(c)
    return s

def from_associationrule(obj):
    s = ''
    if obj.cardinality[0] != 1:
        s += 'minRet = %i; ' % obj.cardinality[0]
    if obj.cardinality[1] != 1:
        s += 'maxRet = %i; ' % obj.cardinality[1]
    s += 'select file as %s from %s where %s;' % (obj.name, obj.datasource, 
                                                  from_expression(obj.condition))
    return s

def from_productdef(obj):
    s = 'product %s' % obj.name
    if obj.assignments:
        s +=' {'
        for a in obj.assignments:
            s += ' %s' % from_assignment(a)
        s +=' }'
    else:
        s +=';'
    return s

def from_recipedef(obj):
    s = 'recipe %s' % obj.name
    if obj.param:
        s += ' {'
        for p, v in obj.param.items():
            s += ' "--%s=%s";' % (p,v) 
        s += ' }'
    else:
        s +=';'
    return s

def from_actionrule(obj):
    s = 'action %s {\n' % obj.name
    for a in obj.associations:
        s += '  %s\n' % from_associationrule(a)
    if obj.recipedef:
        s += '  %s\n' % from_recipedef(obj.recipedef)
    for p in obj.products:
        s += '  %s\n' % from_productdef(p)
    s += '}\n'
    return s

def from_ocaorganizer(obj):
    s = from_classificator(obj.classify) + from_organizator(obj.group)
    for a in obj.action.values():
        s += from_actionrule(a)
    return s

def to_oca(obj):
    functions = {
        organizer.Expression: from_expression,
        organizer.Assignment: from_assignment,
        organizer.ClassificationRule: from_classificationrule,
        organizer.Classificator: from_classificator,
        organizer.OrganizationRule: from_organizationrule,
        organizer.Organizator: from_organizator,
        organizer.AssociationRule: from_associationrule,
        organizer.ProductDef: from_productdef,
        organizer.RecipeDef: from_recipedef,
        organizer.ActionRule: from_actionrule,
        organizer.OcaOrganizer: from_ocaorganizer,
        }
    for cls, func in functions.items():
        if isinstance(obj, cls):
            return func(obj)
    
