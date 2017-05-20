from custom.profile import ProfileReader
from bbgum.frame import Action, Frame, FrameError

import multiprocessing
import socket
import os

class BbGumServerError(Exception):
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

class BbGumServer(object):

    __HOST = ''     # Symbolic name meaning all available interfaces
    __QCON_MAX = 5  # Maximum number of queued connections

    def __init__(self, logger, config_prof, port):
        self.logger = logger
        self.port = port

        try:
            reader = ProfileReader(self.logger)
            proftree = reader(config_prof)
        except:
            msg = 'Problems came up when reading configuration profile'
            raise BbGumServerError(msg)


    def start(self):
        """start the service upon selected port"""

        def listener():
            self.logger.debug("listening")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.__HOST, self.port))
            self.socket.listen(self.__QCON_MAX)

        def spawner():
            print('Use Control-C to exit')
            while True:
                conn, address = self.socket.accept()
                self.logger.debug("Got connection")
                process = multiprocessing.Process(
                    target=self.read_frame, args=(conn, address))
                process.daemon = True
                process.start()
                self.logger.debug("Started process %r", process)

        def shutdown():
            self.logger.info("Shutting down")
            for process in multiprocessing.active_children():
                self.logger.info("Shutting down process %r", process)
                process.terminate()
                process.join()

        try:
            listener()
            spawner()
        except KeyboardInterrupt:
            print('Exiting')
        except BbGumServerError as e:
            raise
        except Exception as e:
            raise
        finally:
            shutdown()

    def __read_socket(self, c, s):
        d = c.recv(s)
        if d == b'':
            raise RuntimeError("socket connection broken")

    def read_frame(self, conn, addr):
        read_header = lambda : self.__read_socket(conn, Frame.FRAME_HEADER_LENGTH)
        read_body = lambda hs: self.__read_socket(conn, hs)
        try:
            self.logger.debug("Connected %r at %r", conn, addr)
            while True:
                self.mon.recive(
                    Action(read_body(Frame.decode_header(read_header())))
                )
        except (RuntimeError, FrameError) as e:
            self.logger.exception(e)
        except:
            self.logger.exception("Problem handling request")
        finally:
            self.logger.debug("Closing socket")
            conn.close()

    class Monitor(object):
        '''
        Entity to deal with incomming/outcomming transaction
        '''
        TRANSACTION_NUM_START_VALUE = 2
        TRANSACTION_NUM_LAST_VALUE = 254
        TRANSACTION_NUM_INCREMENT = 2
        MAX_NODES = 256

        next_num = TRANSACTION_NUM_START_VALUE
        pool = [None] * MAX_NODES
