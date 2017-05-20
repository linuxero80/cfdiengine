class Monitor(object):
    '''
    Entity to deal with incomming/outcomming transactions
    '''
    TRANSACTION_NUM_START_VALUE = 2
    TRANSACTION_NUM_LAST_VALUE = 254
    TRANSACTION_NUM_INCREMENT = 2
    MAX_NODES = 256

    # Initialization of elements for transactions pool
    next_num = TRANSACTION_NUM_START_VALUE
    pool = [None] * MAX_NODES
    pool_lock = threading.Lock()

    def __init__(self, logger, conn, factory):
       self.logger = logger
       self.conn = conn
       self.factory = factory

    def recive(self, a):
        if not self.factory.is_supported(a.archetype):
            pass
