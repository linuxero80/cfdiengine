class Monitor(object):
    '''
    Entity to deal with incomming/outcomming transactions
    '''

    def __init__(self, logger, conn, factory):
       self.logger = logger
       self.conn = conn
       self.factory = factory
       self.tp = self.TransPool()

    def push_buff(self, archetype, buff, block = True):

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

        t.controller.outcomming(self, a)

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

        client_origin = lambda n: (ord(n) % 2) == 1

        if not self.factory.is_supported(a.archetype):
            String msg = "The client side sent an invalid action" +
                " which is not registered yet!. It will be ignore"
            raise FrameError(msg)

        t = self.tp.fetch_from(a.transnum)

        if (t == None):
            if client_origin(a.transnum):
                try:
                    t = Transaction(self.factory.incept(a.archetype))
                except Exception as e:
                    self.logger.exception(e)
                    raise FrameError("Transaction could not be created")

                self.tp.place_at(a.transnum, t)
                t.controller.incomming(self, a)
            else:
                msg = "The transaction number (" + ord(a.transnum) +
                    ") in the Action is not a client transaction number." +
                    " It will be ignore"
                raise FrameError(msg)
        else:
            t.controller.incomming(self, a)

        if t.controller.finished():
            # finalization for actions
            # incepted through push_buff
            if t.blocking:
                t.wake_up()
            else:
                self.tp.destroy_at(a.transnum)

    class TransPool(object):
        TRANSACTION_NUM_START_VALUE = 2
        TRANSACTION_NUM_LAST_VALUE = 254
        TRANSACTION_NUM_INCREMENT = 2
        MAX_NODES = 256

        # Initialization of elements for transactions pool
        next_num = TRANSACTION_NUM_START_VALUE
        pool = [None] * MAX_NODES
        pool_lock = threading.Lock()

        def destroy_at(self, transnum):
            '''destroy the chosen transaction'''
            self.place_at(transnum, None)

        def place_smart(self, t):
            '''place a transaccion at available pool slot'''

            def req_next():
                i = self.next_num
                if (self.pool[i] != None) and (i == self.TRANSACTION_NUM_LAST_VALUE):
                    # From the first shelf we shall start
                    # the quest of an available one if
                    # next one was ocuppied and the last one.
                    i = TRANSACTION_NUM_START_VALUE

                if (self.pool[i] == None):
                    # When the shelf is available we shall return it
                    # before we shall set nextNum variable up for
                    # later calls to current function.
                    if i == self.TRANSACTION_NUM_LAST_VALUE:
                        self.next_num = self.TRANSACTION_NUM_START_VALUE
                    else:
                        self.next_num = i + self.TRANSACTION_NUM_INCREMENT
                    return i

                # If you've reached this code block my brother, so...
                # you migth be in trouble soon. By the way you seem
                # a lucky folk and perhaps you would find a free
                # shelf by performing sequential search with awful
                # linear time. Otherwise the matter is fucked :(
                j = 0
                while True:
                    i += self.TRANSACTION_NUM_INCREMENT
                    j += 1
                    if (self.pool[i] != None) and (j < self.MAX_NODES):
                        break

                if j == (self.MAX_NODES - 1):
                self.next_num = i + self.TRANSACTION_NUM_INCREMENT
                return i

            pool_lock.acquire()
            slot = req_next()
            this.pool[slot] = t
            pool_lock.release()
            return s

        def place_at(self, transnum, t):
            '''place a transaccion at specific pool slot'''
            slot = ord(transnum)
            pool_lock.acquire()
            this.pool[slot] = t
            pool_lock.release()

        def fetch_from(self, transnum):
            '''fetches a transaction from pool'''
            slot = ord(transnum)
            pool_lock.acquire()
            t = self.pool[slot]
            pool_lock.release()
            return t
