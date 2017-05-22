class Factory(object):
    '''
    '''
    __s = {}

    def __init__(self):
        pass

    def is_supported(self, i):
        ic = self.__s.get(i, None)
        return False if not ic else True

    def subscribe(self, i, ic):
        self.__s[i] = ic

    def incept(self, i):
        ic = self.__s.get(i, None)
        return None if not ic else ic()
