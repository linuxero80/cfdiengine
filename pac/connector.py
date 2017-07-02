from custom.profile import ProfileReader
from misc.tricks import dict_params
from pac.servisim import Servisim


class PacChannelError(Exception):
    def __init__(self, message = None):
        self.message = message

    def __str__(self):
        return self.message


class PacSupplierError(PacChannelError):
    def __init__(self, message = None, target = None):
        self.target = target
        super().__init__(message = message)


def pac_channel(logger, conf, xml, **kwargs):
    """
    Produces a newer xml signed by a pac selected
    """
    support = {
        'servisim': dict(test=(Servisim, conf.test), real=(Servisim, conf.real))
    }

    name = ProfileReader.get_content(conf.name, ProfileReader.PNODE_UNIQUE)
    mode = ProfileReader.get_content(conf.mode, ProfileReader.PNODE_UNIQUE)
    supplier = support.get(name.lower(), None)

    if supplier is not None:
        adapter = None
        try:
            ic, settings = supplier[mode]
            return ic(
                logger, **dict_params(
                    ProfileReader.get_content(
                        settings,
                        ProfileReader.PNODE_MANY
                    ),
                    "param", "value")
            )
        except KeyError:
            msg = "Such pac mode is not supported"
            raise PacSupplierError(msg)

        adapter.stamp(xml, xid)
    else:
        raise PacSupplierError("Such pac is not supported yet")

