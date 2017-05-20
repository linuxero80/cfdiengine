from bbgum.factory import Factory
from custom.profile import ProfileTree, ProfileReader
from misc.tricks import dict_params
from misc.singmeta import SingMeta

class AppCtx(object):
    '''
    Singleton object to work as a mediator of
    shared data among core entities
    '''
    __metaclass__ = SingMeta
    def __init__(self, pt):
        self.pt = pt

    def make_factory(self):
        devents = dict_params(
            ProfileReader.get_content(
            self.bbgum.events,
            ProfileReader.PNODE_MANY)
        )
        fact = Factory()
        for archetype, m in devents.items():
            emod = __import__(m)
            cname = getattr(emod, "impt_class")
            ic = getattr(emod, cname)
            fact.subscribe(archetype, ic)
        return fact
