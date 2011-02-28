import organizer

class CplRules(organizer.OcaOrganizer):
    def __init__(self, recipelist):
        self.external_name = 'externalFiles'
        self.inputs_name = 'inputFiles'
        self.products_name = 'products'
        self.calibs_name = 'calibFiles'

        self.recipes = set()
        self.inputs = set()
        self.calibs = set()
        self.products = set()
        
        for r in recipelist:
            if not r.tags:
                continue
            self.recipes.update((r, tag) for tag in r.tags)
            self.inputs.update(r.tags)
            self.calibs.update(c.tag for c in r.calib)
            for tag in r.tags:
                self.products.update(r.output(tag))
        
        self.inputs.difference_update(self.products)
        self.external = set(self.calibs)
        self.external.difference_update(self.products)
        self.calibs.intersection_update(self.products)
        self.products.difference_update(self.calibs)

    def get_source(self, tag):
        return self.external_name if tag in self.external else \
            self.inputs_name if tag in self.inputs else \
            self.products_name if tag in self.products else \
            self.calibs_name if tag in self.calibs else \
            None

    def get_keyword(self, tag):
        return {
            self.external_name:'DO.CATG',
            self.inputs_name:'DO.CATG',
            self.products_name:'PRO.CATG',
            self.calibs_name:'PRO.CATG',
            }[self.get_source(tag)]

    def get_tag_condition(self, tag, fitskey = None):
        return organizer.Expression('==', [ 
                organizer.FitsKeyword(fitskey or self.get_keyword(tag)), 
                organizer.Constant(tag)
                ])

    def get_tag_assignment(self, tag):
        return [ organizer.Assignment(self.get_keyword(tag), 
                                      organizer.Constant(tag)) ]
    
    def get_action_name(self, recipe, tag):
        return '%s_%s' % (recipe.name.upper(), tag) if len(recipe.tags) > 1 \
            else '%s' % recipe.name.upper()

    @property
    def classifications(self):
        return [
            organizer.ClassificationRule(self.get_tag_condition(tag, 'OBJECT'), 
                                         self.get_tag_assignment(tag) )
            for tag in self.inputs ] + [
            organizer.ClassificationRule(self.get_tag_condition(tag, 'DPR.TYPE'),
                                         self.get_tag_assignment(tag) )
            for tag in self.external ]
    
    @property
    def groups(self):
        return [  organizer.OrganizationRule(self.get_action_name(r, tag), 
                                               self.get_source(tag), 
                                               self.get_tag_condition(tag), 
                                               [], [])
                  for r, tag in self.recipes ]

    @property
    def action(self):
        return dict((self.get_action_name(r, tag), CplActionRule(self, r, tag)) 
                    for r, tag in self.recipes)

class CplActionRule(organizer.ActionRule):
    def __init__(self, organizer, recipe, tag):
        self.parent = organizer
        self.recipe = recipe
        self.tag = tag

    @property
    def name(self):
        return self.parent.get_action_name(self.recipe, self.tag)

    @property
    def associations(self):
        return [ organizer.AssociationRule(c.tag, 
                                           self.parent.get_source(c.tag), 
                                           self.parent.get_tag_condition(c.tag),
                                           (max(c.min or 0, 0), c.max))
                 for c in self.recipe.calib ]

    @property
    def recipedef(self):
        return organizer.RecipeDef(self.name, dict((p.name, p.value) 
                                                   for p in self.recipe.param 
                                                   if p.value is not None))

    @property
    def products(self):
        return [ organizer.ProductDef(p, self.parent.get_tag_assignment(p))
                 for p in self.recipe.output(self.tag) ]

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
    newr = []
    while len(recipes) > 0:
        for r, tag in recipes:
            if tag in available and calib_available(r, available):
                newr.append((r, tag))
                available.update(r.output(tag))
        recipes.difference_update(newr)
    return newr


