class Action(object):

    def __init__(self):
        self.id = b'\x00'
        self.transnum = b'\x00'
        self.data = bytearray()
