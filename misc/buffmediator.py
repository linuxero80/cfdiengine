from misc.slackpool import SlackPool

class BuffMediator(object):

    IN_STREAM, OUT_STREAM = range(2)
    read = 0 # bytes read during transfer

    def __init__(self):
        self.sp = SlackPool(start_value=1, last_value=10,
                            increment=1, max=11)

    def mediate(self, sense, size, on_ready):
        t = {'SENSE': sense, 'SIZE': size, 'ON_READY': on_ready}
        self.sp.place_smart(t):

    def release(self, sid):
        self.sp.destroy_at(sid)

    def write_rawbuff(self, sid, data):
        pass

    def read_rawbuff(self, sid, length):
        pass
