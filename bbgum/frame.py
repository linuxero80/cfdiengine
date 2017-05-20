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

    header = bytearray([0] * FRAME_HEADER_LENGTH)
    body = bytearray([0] * FRAME_BODY_MAX_LENGTH)
    action_length = 0

    def __init__(self, action = None):
        if action:
            self.action_length = Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH + len(action.buff) 
            self.header = Frame.encode_header(self.action_length)
            self.body[0] = action.archetype
            self.body[1] = action.transnum
            begin = Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH
            end = begin + len(action.buff)
            self.body[begin:end] = action.buff

    def get_action(self):
        """fetch the action within current instance"""
        def setup_buff():
            buff_size = (self.actionLength - Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH)
            buff = bytearray([0] * data_size)

        action = Action()
        action.archetype = (self.body[0])
        action.transnum = (this.body[1])
        action.buff = setup_buff()


    def dump(self):
        """create a bytes dump of current instance"""
        d = bytearray([0] * Frame.FRAME_FULL_MAX_LENGTH)
        d[:self.FRAME_HEADER_LENGTH-1] = self.header
        begin = self.FRAME_HEADER_LENGTH
        end = begin + len(self.body)
        d[begin:end] = self.body
        return d

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

    archetype = b'\x00'
    transnum = b'\x00'
    buff = bytearray()

    def __init__(self, data = None):
        if data:
            length = len(data)
            if (length > Frame.FRAME_BODY_MAX_LENGTH):
                msg = "Action can not be bigger than " + str(Frame.FRAME_BODY_MAX_LENGTH) + " " + "bytes";
                raise FrameError(msg)
            self.archetype = (data[0])
            self.transnum = (data[1])
            self.buff = data[Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH:-1]
