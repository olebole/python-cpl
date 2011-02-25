import rawrules
import organizer

def CplRules(recipelist):
    return organizer.OcaOrganizer(RawCplRules(recipelist))

class RawCplRules(object):
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
        return rawrules.Expression('==', [ 
                rawrules.Expression('FitsKeyword', 
                                    [ fitskey or self.get_keyword(tag)]), 
                tag
                ])

    def get_tag_assignment(self, tag):
        return [ rawrules.Assignment(self.get_keyword(tag), tag) ]
    
    def get_action_name(self, recipe, tag):
        return '%s_%s' % (recipe.name.upper(), tag) if len(recipe.tags) > 1 \
            else '%s' % recipe.name.upper()

    @property
    def classification(self):
        return [
            rawrules.ClassificationRule(self.get_tag_condition(tag, 'OBJECT'), 
                                        self.get_tag_assignment(tag) )
            for tag in self.inputs ] + [
            rawrules.ClassificationRule(self.get_tag_condition(tag, 'DPR.TYPE'),
                                        self.get_tag_assignment(tag) )
            for tag in self.external ]
    
    @property
    def grouping(self):
        return [  rawrules.GroupingRule(self.get_action_name(r, tag), 
                                        self.get_source(tag), 
                                        self.get_tag_condition(tag), [], [])
                  for r, tag in self.recipes ]

    @property
    def actions(self):
        action_rules = []
        for r, tag in self.recipes:
            calibs = [ rawrules.AssociationRule(c.tag, self.get_source(c.tag), 
                                                self.get_tag_condition(c.tag),
                                                (max(c.min or 0, 0), c.max))
                       for c in r.calib ]
                
            products = [ rawrules.ProductDefinition(p,self.get_tag_assignment(p))
                         for p in r.output(tag) ]
        
            name = self.get_action_name(r, tag)
            rec = rawrules.RecipeDefinition(r.name, [])
            action_rules.append(rawrules.ActionRule(name, calibs, rec, products))
        
        return action_rules


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


