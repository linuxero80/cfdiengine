from misc.slackpool import SlackPool


class BuffMediator(object):

    IN_STREAM, OUT_STREAM = range(2)

    def __init__(self):
        self.sp = SlackPool(start=1, last=10,
                            increment=1, reset=11)

    def mediate(self, sense, size, on_release):
        m = {
            'BUFF': bytearray(),
            'SENSE': sense,
            'SIZE': size,
            'READ': 0,
            'WRITTEN': 0,
            'ON_RELEASE': on_release
        }
        return self.sp.place_smart(m)

    def release(self, sid):
        m = self.sp.fetch_from(sid)
        self.sp.destroy_at(sid)
        return m['ON_RELEASE'](m['BUFF'])

    def write(self, sid, data):
        self.sp.fetch_from(sid)

    def read(self, sid, length):
        self.sp.fetch_from(sid)
