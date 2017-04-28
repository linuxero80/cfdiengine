import random
import string

class HelperStr(object):

    @staticmethod
    def random_str(size):
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(size)
        )
