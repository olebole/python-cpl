import collections
import subprocess

Expression = collections.namedtuple('Expression' ,
    'op param')
ClassificationRule = collections.namedtuple('ClassificationRule',
    'condition assignments')
Assignment = collections.namedtuple('Assignment',
    'target expression')
GroupingRule = collections.namedtuple('GroupingRule',
    'actionname dataset condition grouping alias')
RecipeDefinition = collections.namedtuple('RecipeDefinition',
    'name parameters')
AssociationRule = collections.namedtuple('AssociationRule',
    'name datasource condition cardinality')
ActionRule = collections.namedtuple('ActionRule',
    'name associations recipe products')
ProductDefinition = collections.namedtuple('ProductDefinition',
    'name assignments')
OCARules = collections.namedtuple('OCARules',
    'classification grouping actions')

def parseFile(fname):
        return parse('_OCAFile', 
            subprocess.Popen(['/usr/bin/cpp', fname], 
                stdout = subprocess.PIPE).stdout.read())


%%

parser oca:
  ignore:    '[ \r\t\n]+'
  ignore:    '#.*?\r?\n'    # line comment
  ignore:    '//.*?\r?\n'    # line comment
  token END: '$'

  token BoolConst: '(True|False)'
  token IntConst: '-?[0-9]+'
  token FloatConst: '-?[0-9]+\\.[0-9]*(e-?[0-9]+)?'
  token StringConst: '"([^\\"]+|\\\\.)*"'
  token nstr: '([^\\"]+|\\\\.)*'

  token FitsKeyword: '[a-zA-Z_][a-zA-Z0-9\\._-]*'
  token name: '[a-zA-Z][a-zA-Z0-9_]*'
  token datasource: '[a-zA-Z][a-zA-Z0-9_\\.]*'

  rule Term: BoolConst {{ return bool(BoolConst) }}
    | FloatConst {{ return float(FloatConst) }}
    | IntConst {{ return int(IntConst) }}
    | StringConst {{ return StringConst[1:-1] }}
    | 'undefined' {{ return None }}
    | FitsKeyword {{ return Expression('FitsKeyword', [ FitsKeyword ]) }}
    | '\(' _Expression '\)' {{ return _Expression }}

  rule _MultOp: Term {{ res = Term }}
    ( ('\*' {{ func = '*' }}
    | '/' {{ func = '/' }}
    | '%' {{ func = '%' }}
    ) Term {{ res = Expression(func, [res, Term]) }}
    )* {{ return res }}

  rule _AddOp: _MultOp {{ res = _MultOp }}
    ( ( '\+' {{ func = '+' }}
    | '-' {{ func = '-' }}
    ) _MultOp {{ res = Expression(func, [res, _MultOp]) }}
    )* {{ return res }}

  rule _RelOp: _AddOp {{ res = _AddOp }}
    ( ( '==' {{ func = '==' }}
    | '!='  {{ func = '!=' }}
    | '\?='  {{ func = '?=' }}
    | '<'  {{ func = '<' }}
    | '<='  {{ func = '<=' }}
    | '>='  {{ func = '>=' }}
    | '>'  {{ func = '>' }}
    | 'like'  {{ func = 'like' }}
    | 'is' {{ func = 'is' }}
    ) _AddOp {{ res = Expression(func, [res, _AddOp]) }}
    )* {{ return res }}

  rule _AndOp: _RelOp {{ res =  [ _RelOp ]}}
     ( 'and' _RelOp   {{ res.append(_RelOp) }}
     )* {{ return res[0] if len(res) == 1 else Expression('and', res) }}

  rule _Expression: _AndOp {{ res = [ _AndOp ] }}
     ( 'or' _RelOp   {{ res.append(_RelOp) }}
     )* {{ return res[0] if len(res) == 1 else Expression('or', res) }}

  rule _IfStatement: 'if' _Expression 'then' {{ cond = _Expression }}
     {{ assignment = [] }}
     ( _Assignment {{ assignment.append(_Assignment) }}
     | '{' 
     ( _Assignment {{ assignment.append(_Assignment) }}
     )* 
     '}' ) {{ return ClassificationRule(cond, assignment) }}

  rule _SelectExecuteStatement: 
     'select execute' '\(' 
     name   {{ xn = name }}
     '\)' 'from' name  {{ src = name }}
     'where' _Expression {{ cond = _Expression }}
     {{ keys = [] }}
     {{ alias = [] }}
     [ 'group' 'by' FitsKeyword {{ keys.append(FitsKeyword) }}
     (',' FitsKeyword )* {{ keys.append(FitsKeyword) }}
     ] 
     [ 'as' '\(' FitsKeyword  {{ alias.append(FitsKeyword) }}
       (',' FitsKeyword {{ alias.append(FitsKeyword) }}
            )*'\)' ]
     ';' {{ return GroupingRule(xn, src, cond, keys, alias) }}

  rule _SelectAssociateStatement: 
     {{ minRet = 1 }}
     {{ maxRet = 1 }}
     [ 'minRet' '=' _Expression ';' {{ minRet = _Expression }} ]
     [ 'maxRet' '=' _Expression ';' {{ maxRet = _Expression }} ]
     'select file' 'as' name 'from' datasource  'where' _Expression ';' 
      {{ return AssociationRule(name, datasource, _Expression, (minRet, maxRet)) }}
     
  rule _Assignment: FitsKeyword '=' _Expression ';' 
     {{ return Assignment(FitsKeyword, _Expression) }}

  rule _RecipeDefinition: 'recipe' name 
     {{ param = dict() }}
     (';' | 
     ('{' 
     ( '"--' 
     FitsKeyword '=' nstr {{ param[FitsKeyword] = nstr }}
     '"' ';' 
      )* 
     '}') )
     {{ return RecipeDefinition(name, param) }}

  rule _ProductDefinition: 'product' name '{' 
     {{ assignment = [] }}
     ( _Assignment {{ assignment.append(_Assignment) }}
     )* 
     '}' {{ return ProductDefinition(name, assignment) }}

  rule _ActionRule: 'action' name '{'  
     {{ assoc = [] }}
     {{ product = [] }}
     {{ recipe = None }}
    ( _SelectAssociateStatement 
            {{ assoc.append(_SelectAssociateStatement) }}
    | _RecipeDefinition {{ recipe = _RecipeDefinition }}
    | _ProductDefinition {{ product.append(_ProductDefinition) }}
    )*
    '}' {{ return ActionRule(name, assoc, recipe, product) }}

  rule _OCAFile: {{ res = OCARules([], [], []) }}
     ( _IfStatement {{ res.classification.append(_IfStatement) }}
     | _SelectExecuteStatement  
            {{ res.grouping.append(_SelectExecuteStatement) }}
     | _ActionRule {{ res.actions.append(_ActionRule) }}
     )* END {{ return res }}

     
