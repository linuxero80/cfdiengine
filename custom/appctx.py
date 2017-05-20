class AppCtx(object):
    '''
    Singleton object to work as a mediator of
    shared data among core entities
    '''
    __metaclass__ = SingMeta
    def __init__(self, pt):
        self.pt = pt
