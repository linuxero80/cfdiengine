from bbgum.factory import Factory
from custom.profile import ProfileTree, ProfileReader
from misc.tricks import dict_params
from misc.singmeta import SingMeta
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(
        os.path.dirname(__file__), "events")))

class AppCtx(object):
    '''
    Singleton object to work as a mediator of
    shared data among core entities
    '''
    __metaclass__ = SingMeta
    def __init__(self, logger, pt):
        self.logger = logger
        self.pt = pt

    def make_factory(self):
        devents = dict_params(
            ProfileReader.get_content(
            self.pt.bbgum.events,
            ProfileReader.PNODE_MANY),
            'archetype', 'event_mod'
        )
        fact = Factory()
        for archetype, event_mod in devents.items():
            try:
                m = __import__(event_mod)

                if not hasattr(m, "impt_class"):
                    msg = "module {0} has no impt_class attribute".format(event_mod)
                    raise RuntimeError(msg)
                cname = getattr(m, "impt_class")

                if not hasattr(m, cname):
                    msg = "module {0} has no {1} class implemented".format(event_mod, cname)
                    raise RuntimeError(msg)
                ic = getattr(m, cname)
                fact.subscribe(archetype, ic)
            except (ImportError, RuntimeError) as e:
                self.logger.fatal("{0} support library failure".format(event_mod))
                raise e
        return fact
