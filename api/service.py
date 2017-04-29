from custom.profile import ProfileReader
import os

class CfdiEngineError(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

class CfdiEngine(object):

    def __init__(self, logger, config_file, port):
        self.logger = logger
        self.port = port

        try:
            reader = ProfileReader(self.logger)
            proftree = reader(config_file)

        except:
            msg = "Problems came up through initialization of api"
            raise CfdiEngineError(msg)

    def start(self):
        "start the service upon selected port"
