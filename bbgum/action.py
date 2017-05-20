from bbgum.frame import FrameError, Frame

class Action(object):

    self.archetype = b'\x00'
    self.transnum = b'\x00'
    self.buffer = bytearray()

    def __init__(self, data = None):
        byteszero = lambda n: bytearray([0] * n)
        if data:
            length = len(data)
            if (length) > Frame.FRAME_BODY_MAX_LENGTH):
                msg = "Action can not be bigger than " + str(Frame.FRAME_BODY_MAX_LENGTH) + " " + "bytes";
                raise FrameError(msg)
            self.archetype = (data[0])
            self.transnum = (data[1])
            self.buffer = data[Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH:-1]
