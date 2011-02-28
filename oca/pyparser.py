import subprocess
import pyparsing

import organizer

# define grammar
_StringConst = pyparsing.quotedString.copy()
_StringConst.setParseAction(lambda token: [ organizer.Constant(token[0][1:-1]) ])

_BoolConst = pyparsing.Keyword('True') | pyparsing.Keyword('False')
_BoolConst.setParseAction(lambda token: [ organizer.Constant(bool(token[0])) ])

_IntConst = pyparsing.Word(pyparsing.nums + '+-', pyparsing.nums)
_IntConst.setParseAction(lambda token: [ organizer.Constant(int(token[0])) ])

_FloatConst = pyparsing.Combine( 
    _IntConst + pyparsing.Literal('.') + 
    pyparsing.Optional( pyparsing.Literal('.') +
                        pyparsing.Optional(pyparsing.Word(pyparsing.nums)) ) +
    pyparsing.Optional( pyparsing.CaselessLiteral('E') + _IntConst ) )
_FloatConst.setParseAction(lambda token: [ organizer.Constant(float(token[0])) ])

_FitsKeyword = pyparsing.Word(pyparsing.alphas, pyparsing.alphanums + '_-.') 
_FitsKeyword.setParseAction(lambda token: [ organizer.FitsKeyword(token[0]) ])

_name = pyparsing.Word(pyparsing.alphas, pyparsing.alphanums + '_')
_datasource = pyparsing.Word(pyparsing.alphas, pyparsing.alphanums + '._') 

_undefined = pyparsing.CaselessLiteral('undefined')
_undefined.setParseAction(lambda tokens: [ None ])

_Expression = pyparsing.Forward()

_Term = ( 
    _BoolConst ^
    _FloatConst ^
    _IntConst ^
    _StringConst ^
    _undefined ^
    _FitsKeyword ^
    ( pyparsing.Literal('(').suppress() + 
      _Expression + 
      pyparsing.Literal(')').suppress() ) 
    )

def _OpAction(tokens):
    expr = tokens.pop(0)
    while len(tokens) > 0:
        expr = organizer.Expression(tokens.pop(0), [expr, tokens.pop(0)])
    return [ expr ]

_MultOp = (
    _Term + pyparsing.ZeroOrMore((pyparsing.Literal('*') ^
                                  pyparsing.Literal('/') ^ 
                                  pyparsing.Literal('%')) + _Term )
    )
_MultOp.setParseAction(_OpAction)

_AddOp = (
    _MultOp + pyparsing.ZeroOrMore((pyparsing.Literal('+') ^ 
                                    pyparsing.Literal('-')) + _MultOp )
    )
_AddOp.setParseAction(_OpAction)

_RelOp = (
    _AddOp + pyparsing.Optional((pyparsing.Literal('==') ^
                                 pyparsing.Literal('!=') ^
                                 pyparsing.Literal('?=') ^
                                 pyparsing.Literal('<') ^
                                 pyparsing.Literal('<=') ^
                                 pyparsing.Literal('>=') ^
                                 pyparsing.Literal('>') ^
                                 pyparsing.CaselessLiteral('like') ^
                                 pyparsing.CaselessLiteral('is'))  + 
                                _AddOp )
    )
_RelOp.setParseAction(_OpAction)

_AndOp = (
    _RelOp + pyparsing.ZeroOrMore(pyparsing.CaselessLiteral('and') + _RelOp )
    )
_AndOp.setParseAction(_OpAction)

_Expression << (
    _AndOp + pyparsing.ZeroOrMore((pyparsing.CaselessLiteral('or') ) + _AndOp)
    )
_Expression.setParseAction(_OpAction)

_Assignment = ( 
    _FitsKeyword + pyparsing.Literal('=').suppress() + 
    _Expression + pyparsing.Literal(';').suppress() 
    )
_Assignment.setParseAction(lambda tokens: [ 
        organizer.Assignment(tokens[0].name, tokens[1]) ])

_AssignmentBlock = pyparsing.Group(_Assignment) | (
    pyparsing.Literal('{').suppress() + 
    pyparsing.Group(pyparsing.ZeroOrMore(_Assignment)) + 
    ( pyparsing.Literal('}').suppress() ) 
    )
_IfStatement = ( 
    pyparsing.CaselessLiteral('if').suppress() + _Expression + 
    pyparsing.CaselessLiteral('then').suppress() + _AssignmentBlock
    )
_IfStatement.setParseAction(lambda tokens: 
                            [ organizer.ClassificationRule(tokens[0], tokens[1])])

_FitsKeywordList = pyparsing.Group(
    _FitsKeyword + 
    pyparsing.ZeroOrMore(pyparsing.Literal(',').suppress() 
                         + _FitsKeyword)
    )
_SelectExecuteStatement = ( 
    pyparsing.CaselessLiteral('select execute').suppress() + 
    pyparsing.Literal('(').suppress() + 
    _name + 
    pyparsing.Literal(')').suppress()  + 
    pyparsing.CaselessLiteral('from').suppress() + _name + 
    pyparsing.CaselessLiteral('where').suppress() + _Expression + 
    pyparsing.Optional(pyparsing.CaselessLiteral('group by') +
                       _FitsKeywordList) +
    pyparsing.Optional(pyparsing.CaselessLiteral('as') + 
                       pyparsing.Literal('(').suppress() + 
                       _FitsKeywordList +
                       pyparsing.Literal(')').suppress()) + 
    pyparsing.Literal(';').suppress() 
    )
def _SelectExecuteStatementAction(token):
    xn = token.pop(0)
    src = token.pop(0)
    cond = token.pop(0)
    if token and token[0] == 'group by':
        token.pop(0)
        keys = [ a[1][0] for a in token.pop(0) ]
    else:
        keys = list()
    if token and token[0] == 'as':
        token.pop(0)
        alias = [ a[1][0] for a in token.pop(0) ]
    else:
        alias = list()
    return [ organizer.OrganizationRule(xn, src, cond, keys, alias) ]
_SelectExecuteStatement.setParseAction(_SelectExecuteStatementAction)

_SelectAssociateStatement = ( 
    pyparsing.Optional(pyparsing.CaselessLiteral('minRet') + 
                       pyparsing.Literal('=').suppress()  +
                       _Expression + pyparsing.Literal(';').suppress()  ) + 
    pyparsing.Optional(pyparsing.CaselessLiteral('maxRet') + 
                       pyparsing.Literal('=').suppress()  +
                       _Expression + pyparsing.Literal(';').suppress()  ) + 
    pyparsing.CaselessLiteral('select file as').suppress() + _name + 
    pyparsing.CaselessLiteral('from').suppress() + _datasource + 
    pyparsing.CaselessLiteral('where').suppress() + _Expression +
    pyparsing.Literal(';').suppress() 
    )
def _SelectAssociateStatementAction(token):
    if token[0] == 'minRet':
        token.pop(0)
        minRet = token.pop(0).value
    else:
        minRet = 1
    if token[0] == 'maxRet':
        token.pop(0)
        maxRet = token.pop(0).value
    else:
        maxRet = 1
    return [ organizer.AssociationRule(token[0], token[1], token[2], 
                                       (minRet, maxRet)) ]

_SelectAssociateStatement.setParseAction(_SelectAssociateStatementAction)

_ParamString = (
    pyparsing.Literal('--').suppress() + 
    pyparsing.Word(pyparsing.alphanums + '._-') +
    pyparsing.Literal('=').suppress() + 
    pyparsing.Word(pyparsing.printables)
)

_RecipePars = ( 
    pyparsing.Literal('{').suppress() + 
    pyparsing.ZeroOrMore( _StringConst + 
                          pyparsing.Literal(';').suppress() ) +
    pyparsing.Literal('}').suppress()  
    )
def _RecipeParsAction(tokens):
    param = dict()
    for t in tokens:
        p = _ParamString.parseString(t.value)
        param[p[0]] = p[1]
    return [ param ]
_RecipePars.setParseAction(_RecipeParsAction)

_RecipeDefinition = (
    pyparsing.CaselessLiteral('recipe').suppress() + _name + 
    ( pyparsing.Literal(';').suppress() | _RecipePars )
    )
def _RecipeDefinitionAction(tokens):
    name = tokens.pop(0)
    param = tokens[0] if tokens else dict()
    return [ organizer.RecipeDef(name, param) ]
_RecipeDefinition.setParseAction(_RecipeDefinitionAction)

_ProductDefinition = ( 
    pyparsing.CaselessLiteral('product').suppress() + _name + 
    pyparsing.Literal('{').suppress()  + 
    pyparsing.ZeroOrMore(_Assignment) + 
    pyparsing.Literal('}').suppress()  
    ) 
def _ProductDefinitionAction(tokens):
    name = tokens.pop(0)
    return organizer.ProductDef(name, tokens)
_ProductDefinition.setParseAction(_ProductDefinitionAction)

_ActionRule = ( 
    pyparsing.CaselessLiteral('action').suppress() + _name + 
    pyparsing.Literal('{').suppress()  + 
    pyparsing.ZeroOrMore(_SelectAssociateStatement | 
                         _RecipeDefinition |
                         _ProductDefinition) + 
    pyparsing.Literal('}').suppress()  
    )
def _ActionRuleAction(tokens):
    name = tokens.pop(0)
    assoc = list()
    product = list()
    recipe = None
    for t in tokens:
        if isinstance(t, organizer.ProductDef):
            product.append(t)
        elif isinstance(t, organizer.RecipeDef):
            recipe = t
        elif isinstance(t, organizer.AssociationRule):
            assoc.append(t)
    return [ organizer.ActionRule(name, assoc, recipe, product) ]

_ActionRule.setParseAction(_ActionRuleAction)

_OCARules = pyparsing.ZeroOrMore( 
        _IfStatement | 
        _SelectExecuteStatement | 
        _ActionRule
        )
def _OCARulesAction(tokens):
    actions = list()
    classification = list()
    grouping = list()
    for t in tokens:
        if isinstance(t, organizer.ActionRule):
            actions.append(t)
        elif isinstance(t, organizer.ClassificationRule):
            classification.append(t)
        elif isinstance(t, organizer.OrganizationRule):
            grouping.append(t)
    return [ organizer.OcaOrganizer(classification, grouping, actions) ]
_OCARules.setParseAction(_OCARulesAction)
_OCARules.ignore( "//" + pyparsing.restOfLine )
_OCARules.ignore( "#" + pyparsing.restOfLine )
_OCARules.ignore( pyparsing.cStyleComment )

def parseFile(fname):
    s = subprocess.Popen(['/usr/bin/cpp', fname], 
                         stdout = subprocess.PIPE).stdout
    rules = list()
    return _OCARules.parseFile(s)[0]

