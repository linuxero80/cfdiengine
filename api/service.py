from custom.profile import ProfileReader
import os

class CfdiEngineError(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

class CfdiEngine(object):

    __HOST = ''    # Symbolic name meaning all available interfaces

    def __init__(self, logger, config_prof, port):
        self.logger = logger

        try:
            reader = ProfileReader(self.logger)
            proftree = reader(config_prof)
        except:
            msg = 'Problems came up when reading configuration profile'
            raise CfdiEngineError(msg)

        self.server = BbGumServer(self.__HOST, port, self.logger)

    def start(self):
        """start the service upon selected port"""
        try:
            print('Use Control-C to exit')
            self.server.getup()
        except KeyboardInterrupt:
            print('Exiting')
        except BbGumServerError as e:
            self.logger.error(e)
            raise
