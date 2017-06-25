from misc.factory import Factory
from misc.tricks import dict_params
from custom.profile import ProfileReader
from engine.buffmediator import BuffMediator
import os
import json
import sys

from engine.cxc import facturar

sys.path.append(
    os.path.abspath(os.path.join(
        os.path.dirname(__file__), "controllers")))


def do_request(req, adapter=None):
    def apply_adapter():
        if adapter is not None:
            return adapter()
        # So interpret request as json string
        json_lines = req.decode(encoding='UTF-8')
        return json.loads(json_lines)

    d = apply_adapter()
    return facturar(d)


class ControllerFactory(Factory):
    def __init__(self, logger, profile_path):
        super().__init__()
        self.logger = logger
        self.bm = BuffMediator()
        pt = self.__read_settings(profile_path)
        self.__makeup_factory(pt.bbgum.controllers)

    def __read_settings(self, s_file):
        self.logger.debug("looking for config profile file in:\n{0}".format(
            os.path.abspath(s_file)))
        if os.path.isfile(s_file):
            reader = ProfileReader(self.logger)
            return reader(s_file)
        raise Exception("unable to locate the config profile file")

    def __makeup_factory(self, variants):
        devents = dict_params(
            ProfileReader.get_content(
                variants, ProfileReader.PNODE_MANY),
            'archetype', 'event_mod')
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
                self.subscribe(int(archetype, 0), ic)
            except (ImportError, RuntimeError) as e:
                self.logger.fatal("{0} support library failure".format(event_mod))
                raise e

    def incept(self, i):
        ic = self.inceptors.get(i, None)
        return None if ic is None else ic(self.logger, self.bm)
