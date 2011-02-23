import rawrules

def get_tags(recipelist):
    '''Return all tags for a given list of recipes.

    Returns two values: first, a list of all (recipe, input tag) pairs, and
    second a dictionary of all used and produced tags with the tag name as key
    and one of the strings 'externalFiles', 'inputFiles', 'calibFiles', or
    'product' as values. The value indicates the type of the tag.
    '''
    inputs = set()
    calibs = set()
    products = set()

    recipes = set()
    for r in recipelist:
        if not r.tags:
            continue
        inputs.update(r.tags)
        calibs.update(c.tag for c in r.calib)
        for tag in r.tags:
            recipes.add((r, tag))
            products.update(r.output(tag))

    inputs.difference_update(products)
    external = set(calibs)
    external.difference_update(products)
    calibs.intersection_update(products)
    products.difference_update(calibs)
    tags = dict()
    for tag in external:
        tags[tag] = 'externalFiles'
    for tag in inputs:
        tags[tag] = 'inputFiles'
    for tag in products:
        tags[tag] = 'products'
    for tag in calibs:
        tags[tag] = 'calibFiles'
    return recipes, tags

def calib_available(recipe, tags):
    for c in recipe.calib:
        if c.tag not in tags:
            return False
    return True

def order_recipes(recipes, tags):
    '''Order recipes for their dependencies.
    '''
    available = set(tag for tag, type in tags.items() 
                    if type in ('externalFiles', 'inputFiles'))
    newr = list()
    while len(recipes) > 0:
        for r, tag in recipes:
            if tag in available and calib_available(r, available):
                newr.append((r, tag))
                available.update(r.output(tag))
        recipes.difference_update(newr)
    return newr

def parseRecipes(recipes):

    catg_keyword = {
        'externalFiles':'DO.CATG',
        'inputFiles':'DO.CATG',
        'products':'PRO.CATG',
        'calibFiles':'PRO.CATG',
        }

    recipes, tags = get_tags(recipes)

    cl_rules = []
    for tag, tag_type in tags.items():
        fitskeyword = {'inputFiles':'OBJECT', 
                       'externalFiles':'DPR.TYPE'}.get(tag_type)
        if fitskeyword is not None:
            cl_rules.append(rawrules.ClassificationRule(
                    rawrules.Expression('==', 
                                        [ rawrules.Expression('FitsKeyword', 
                                                              [fitskeyword]), 
                                          tag]), 
                    [rawrules.Assignment(catg_keyword[tag_type], tag )]))
            
    grouping_rules = []
    for r, tag in recipes:
        name = '%s_%s' % (r.name.upper(), tag) if len(r.tags) > 1 \
            else '%s' % r.name.upper()
        grouping_rules.append(rawrules.GroupingRule(
                name, tags[tag], 
                rawrules.Expression('==', 
                           [ rawrules.Expression('FitsKeyword', 
                                        [ catg_keyword[tags[tag]]]), tag]), 
                list(), list()))

    action_rules = []
    for r, tag in recipes:
        name = '%s_%s' % (r.name.upper(), tag) if len(r.tags) > 1 \
            else '%s' % r.name.upper()
        calibs = list()
        for c in r.calib:
            calibs.append(rawrules.AssociationRule(c.tag, tags[c.tag], 
                                          rawrules.Expression('==', [ 
                            rawrules.Expression('FitsKeyword',
                                       [catg_keyword[tags[c.tag]]]), c.tag]),
                                          (max(c.min or 0, 0), c.max)))
        products = list()
        for p in r.output(tag):
            products.append(rawrules.ProductDefinition(p,[ 
                        rawrules.Assignment(catg_keyword[tags[p]], p) ]))

        rec = rawrules.RecipeDefinition(r.name, list())
        action_rules.append(rawrules.ActionRule(name, calibs, rec, products))
    
    return rawrules.OCARules(cl_rules, grouping_rules, action_rules)


