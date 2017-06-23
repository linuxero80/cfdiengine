from misc.slackpool import SlackPool

class BuffMediator(object):

    IN_STREAM, OUT_STREAM = range(2)
    read = 0 # bytes read during transfer

    def __init__(self):
        self.sp = SlackPool(start=1, last=10,
                            increment=1, reset=11)

    def mediate(self, sense, size, on_ready):
        t = {
            'SENSE': sense,
            'SIZE': size,
            'READ': 0,
            'WRITTEN': 0,
            'ON_READY': on_ready
        }
        self.sp.place_smart(t):

    def release(self, sid):
        self.sp.destroy_at(sid)

    def write_rawbuff(self, sid, data):
        self.sp.fetch_from(sid)

    def read_rawbuff(self, sid, length):
        self.sp.fetch_from(sid)
