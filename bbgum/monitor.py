class Monitor(object):
    '''
    Entity to deal with incomming/outcomming transactions
    '''

    def __init__(self, logger, conn, factory):
       self.logger = logger
       self.conn = conn
       self.factory = factory
       self.tp = self.TransPool()

    def receive(self, a):
        """receives action from upper layer"""

        if not self.factory.is_supported(a.archetype):
            String msg = "The client side sent an invalid action" +
                " which is not registered yet!. It will be ignore"
            raise FrameError(msg)

        t = self.tp.get_from(a.transnum)

        if (t == None):
            if self.isClientTransaction(a.transnum):
                pass

    def isClientTransaction(self, n):
        return (ord(n) % 2) == 1

    class TransPool(object):
        TRANSACTION_NUM_START_VALUE = 2
        TRANSACTION_NUM_LAST_VALUE = 254
        TRANSACTION_NUM_INCREMENT = 2
        MAX_NODES = 256

        # Initialization of elements for transactions pool
        next_num = TRANSACTION_NUM_START_VALUE
        pool = [None] * MAX_NODES
        pool_lock = threading.Lock()

        def destroy(self, transnum):
            '''destroy the chosen transaction'''
            self.put(transnum, None)

        def push_smart(self, t):
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
                    j++
                    if (self.pool[i] != None) and (j < self.MAX_NODES):
                        break

                if j == (self.MAX_NODES - 1):
                self.next_num = i + self.TRANSACTION_NUM_INCREMENT
                return i

            pool_lock.acquire()
            i = req_next()
            this.pool[i] = t
            pool_lock.release()

        def push_at(self, transnum, t):
            '''place a transaccion at specific pool slot'''
            i = ord(transnum)
            pool_lock.acquire()
            this.pool[i] = t
            pool_lock.release()

        def get_from(self, transnum):
            '''fetches a transaction from pool'''
            t = None
            i = ord(transnum)
            pool_lock.acquire()
            t = self.pool[i]
            pool_lock.release()
            return t

