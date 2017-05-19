from bbgum.frame import FrameError

class Action(object):

    def __init__(self, data = None):
        if data:
            if (len(data) > Frame.FRAME_BODY_MAX_LENGTH):
                msg = "Action can not be bigger than " + str(Frame.FRAME_BODY_MAX_LENGTH) + " " + "bytes";
                raise FrameError(msg)

            self.archetype = (data[0])
            self.transnum = (data[1])
        else:
            self.archetype = b'\x00'
            self.transnum = b'\x00'
            self.buffer = bytearray()
