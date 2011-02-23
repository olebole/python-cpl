import collections

Expression = collections.namedtuple('Expression' , 'op param')
Assignment = collections.namedtuple('Assignment',
    'target expression')
ClassificationRule = collections.namedtuple('ClassificationRule',
    'condition assignments')
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

