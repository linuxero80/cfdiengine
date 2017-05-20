class FrameError(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

class Frame(object):

    FRAME_HEADER_LENGTH = 4
    FRAME_BODY_MAX_LENGTH = 512
    ACTION_FLOW_INFO_SEGMENT_LENGTH = 2
    ACTION_ACK_DATA_SIZE = 2
    FRAME_FULL_MAX_LENGTH = FRAME_HEADER_LENGTH + FRAME_BODY_MAX_LENGTH
    ACTION_DATA_SEGMENT_MAX_LENGTH = FRAME_BODY_MAX_LENGTH - ACTION_FLOW_INFO_SEGMENT_LENGTH
    C_NULL_CHARACTER = 0

    REPLY_PASS = b'\x06'
    REPLY_FAIL = b'\x15'

    def __init__(self):
        byteszero = lambda n: bytearray([0] * n)
        self.header = byteszero(self.FRAME_HEADER_LENGTH)
        self.body = byteszero(self.FRAME_BODY_MAX_LENGTH)
        self.body_length = 0

    @staticmethod
    def encode_header(length):
        if length > Frame.FRAME_BODY_MAX_LENGTH:
            raise FrameError("invalid length to encode!!")
        l = []
        for sc in '{:3d}'.format(length):
            l.append(ord(sc))
        l.append(Frame.C_NULL_CHARACTER)
        return bytes(l)

    @staticmethod
    def decode_header(header):
        cut_nullchar = lambda s: s[:-1] # keep everything except the last item
        if (len(header) == Frame.FRAME_HEADER_LENGTH):
            try:
                return int(cut_nullchar(header).decode("utf-8"))
            except:
                raise FrameError("unexpected problems when decoding header!!")
        raise FrameError("header's width violiation!!")


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
