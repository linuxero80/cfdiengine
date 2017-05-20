class Factory(object):
    '''
    '''
    __s = {}

    def __init__(self):
        pass

    def is_supported(self, archetype):
        ic = self.__s.get(ord(archetype), None)
        return False if not ic else True

    def subscribe(self, archetype, ic):
        self.__s[ord(archetype)] = ic

    def incept(self, archetype):
        ic = self.__s.get(ord(archetype), None)
        return None if not ic else ic()
