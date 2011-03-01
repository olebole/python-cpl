import organizer

class CplClassificationRule(organizer.ClassificationRule):
    def __init__(self, organizer, tag, fitskeyword):
        self.organizer = organizer
        self.tag = tag
        self.fitskeyword = fitskeyword

    @property 
    def condition(self):
        return self.organizer.get_tag_condition(self.tag, self.fitskeyword)

    @property
    def assignments(self):
        return self.organizer.get_tag_assignment(self.tag)

class CplOrganizationRule(organizer.OrganizationRule):
    def __init__(self, organizer, recipe, tag):
        self.organizer = organizer
        self.recipe = recipe
        self.tag = tag
        self.grouping = []
        self.alias = []

    @property
    def actionname(self):
        return self.organizer.get_action_name(self.recipe, self.tag)

    @property
    def condition(self):
        return self.organizer.get_tag_condition(self.tag)

    @property
    def dataset(self):
        return self.organizer.get_source(self.tag)

class CplAssociationRule(organizer.AssociationRule):
    def __init__(self, organizer, framedef):
        self.organizer = organizer
        self.name = framedef.tag
        self.cardinality = (max(framedef.min or 0, 0), 
                            max(framedef.max or 1, 1))

    @property
    def datasource(self):
        return self.organizer.get_source(self.name)

    @property
    def condition(self):
        return self.organizer.get_tag_condition(self.name)

class CplActionRule(organizer.ActionRule):
    def __init__(self, organizer, recipe, tag):
        self.parent = organizer
        self.recipe = recipe
        self.tag = tag
        self.associations = [ CplAssociationRule(organizer, c)
                              for c in self.recipe.calib ]
        self.organizationrule = CplOrganizationRule(organizer, recipe, tag) 

    @property
    def name(self):
        return self.parent.get_action_name(self.recipe, self.tag)

    @property
    def recipedef(self):
        return organizer.RecipeDef(self.name, dict((p.name, p.value) 
                                                   for p in self.recipe.param 
                                                   if p.value is not None))

    @property
    def products(self):
        return [ organizer.ProductDef(p, self.parent.get_tag_assignment(p))
                 for p in self.recipe.output(self.tag) ]

class CplOrganizer(organizer.OcaOrganizer):
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

        self.action =  dict((self.get_action_name(r, tag), 
                             CplActionRule(self, r, tag)) 
                            for r, tag in self.recipes)
        self.classifications = [ 
            CplClassificationRule(self, tag, 'OBJECT') 
            for tag in self.inputs ] + [
            CplClassificationRule(self, tag, 'DPR.TYPE') 
            for tag in self.external ]
            
    @property
    def groups(self):
        return [ a.organizationrule for a in self.action.values() ]

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

# ------------------------------------------------------------------------

if __name__ == "__main__":

    from optparse import OptionParser
    import cpl
    from ocawriter import to_oca

    oparser = OptionParser()
    oparser.add_option('-r', '--path', help = 'MUSE recipe path',
                       default = '/tmp/musetest')
    oparser.add_option('-v', '--version', help = 'Use specified MUSE version')
    oparser.add_option('-o', '--outfile', 
                       help = 'OCA output file (default: stdout)')

    (opt, filenames) = oparser.parse_args()

    cpl.Recipe.path = opt.path
    recipes = [ cpl.Recipe(name, version = opt.version) 
                for name,versions in cpl.Recipe.list() 
                if opt.version is None or opt.version in versions ]

    for r in recipes:
        try:
            r.param.nifu = 0
        except:
            pass

    org = CplOrganizer(recipes)
    if opt.outfile:
        file(opt.outfile, 'w').write(to_oca(org))
    else:
        print to_oca(org)
