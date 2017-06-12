from queue import Queue, Empty
from bbgum.frame import Action, Frame, FrameError
from bbgum.transaction import Transaction
import threading


class Monitor(object):
    """Entity to deal with incoming/outcoming transactions"""

    def __init__(self, logger, conn, factory):
        self.logger = logger
        self.conn = conn
        self.factory = factory
        self.outgoing = Queue(maxsize=0)
        self.tp = self.TransPool()

    def push_buff(self, archetype, buff, block=True):

        def incept_trans():
            try:
                return Transaction(self.factory.incept(archetype), block)
            except Exception as e:
                self.logger.exception(e)
                raise FrameError('Transaction could not be created')

        def makeup_action(transnum):
            act = Action()
            act.archetype = archetype
            act.buff = buff
            act.transnum = transnum
            return act

        t = incept_trans()
        slot = self.tp.place_smart(self, t)
        a = makeup_action(bytes([slot]))

        t.controller.outcoming(self, a)

        if t.blocking:
            try:
                t.sleep()
            except Exception as e:
                self.logger.exception(e)
                raise FrameError('Transaction could not await')

            reply = t.controller.get_reply()
            self.tp.destroy_at(a.transnum)
            # Blocking transaction returns a dictionary
            return reply
        else:
            # Non-blocking transaction returns None
            return None

    def receive(self, a):
        """receives action from upper layer"""

        client_origin = lambda n: (n % 2) == 1

        if (not self.factory.is_supported(
                a.archetype)) and (not self.factory.is_supported(
                a.archetype - 1)):
            msg = '{} {}!'.format(
                'The client side sent an invalid action which',
                'is not registered yet!. It will be ignore'
            )
            raise FrameError(msg)

        t = self.tp.fetch_from(a.transnum)

        if t is None:
            if client_origin(a.transnum):
                try:
                    t = Transaction(self.factory.incept(a.archetype), False)
                except Exception as e:
                    self.logger.exception(e)
                    raise FrameError("Transaction could not be created")

                self.tp.place_at(a.transnum, t)
                t.controller.incoming(self, a)
            else:
                msg = '{} ({}) {}. {}'.format(
                    "The transaction number",
                    ord(a.transnum),
                    'in the Action is not a client transaction number.',
                    "It will be ignore!"
                )
                raise FrameError(msg)
        else:
            t.controller.incoming(self, a)

        if t.controller.finished():
            # finalization for actions
            # incepted through push_buff
            if t.blocking:
                t.wake_up()
            else:
                self.tp.destroy_at(a.transnum)

    def send(self, a):
        """write action upon socket"""

        def release():
            try:
                frame = self.outgoing.get_nowait()
                buff = frame.dump()
                size = len(buff)
                total = 0
                while total < size:
                    sent = self.conn.send(buff[total:])
                    if sent == 0:
                        raise RuntimeError("socket connection broken")
                    total += sent
            except Empty as e:
                self.logger.warning(e)

        available = self.outgoing.empty()
        self.outgoing.put(Frame(a))
        if available:
            while not self.outgoing.empty():
                release()

    class TransPool(object):
        """pool that stores active transactions"""

        TRANSACTION_NUM_START_VALUE = 2
        TRANSACTION_NUM_LAST_VALUE = 254
        TRANSACTION_NUM_INCREMENT = 2
        MAX_NODES = 256

        # Initialization of elements for transactions pool
        next_num = TRANSACTION_NUM_START_VALUE
        pool = [None] * MAX_NODES
        pool_lock = threading.Lock()

        def __init__(self):
            pass

        def destroy_at(self, transnum):
            """destroy the chosen transaction"""
            self.place_at(transnum, None)

        def place_smart(self, t):
            """place a transaction at available pool slot"""

            def req_next():
                i = self.next_num
                if (self.pool[i] is not None) and (i == self.TRANSACTION_NUM_LAST_VALUE):
                    # From the first shelf we shall start
                    # the quest of an available one if
                    # next one was ocuppied and the last one.
                    i = self.TRANSACTION_NUM_START_VALUE

                if self.pool[i] is None:
                    # When the shelf is available we shall return it
                    # before we shall set nextNum variable up for
                    # later calls to current function.
                    if i == self.TRANSACTION_NUM_LAST_VALUE:
                        self.next_num = self.TRANSACTION_NUM_START_VALUE
                    else:
                        self.next_num = i + self.TRANSACTION_NUM_INCREMENT
                    return i

                # If you've reached this code block my brother, so...
                # you might be in trouble soon. By the way you seem
                # a lucky folk and perhaps you would find a free
                # shelf by performing sequential search with awful
                # linear time. Otherwise the matter is fucked :(
                j = 0
                while True:
                    i += self.TRANSACTION_NUM_INCREMENT
                    j += 1
                    if (self.pool[i] is not None) and (j < self.MAX_NODES):
                        break

                if j == (self.MAX_NODES - 1):
                    self.next_num = i + self.TRANSACTION_NUM_INCREMENT
                return i

            self.pool_lock.acquire()
            slot = req_next()
            self.pool[slot] = t
            self.pool_lock.release()
            return slot

        def place_at(self, transnum, t):
            """place a transaction at specific pool slot"""
            slot = transnum
            self.pool_lock.acquire()
            self.pool[slot] = t
            self.pool_lock.release()

        def fetch_from(self, transnum):
            """fetches a transaction from pool"""
            slot = transnum
            self.pool_lock.acquire()
            t = self.pool[slot]
            self.pool_lock.release()
            return t
