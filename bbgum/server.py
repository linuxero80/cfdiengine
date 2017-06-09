from custom.profile import ProfileReader
from bbgum.frame import Action, Frame, FrameError

import multiprocessing
import threading
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

    def __init__(self, queue, profile_path, port):
        self.queue = queue
        self.profile_path = profile_path
        self.port = port

    def start(self):
        """start the service upon selected port"""

        def listener():
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.__HOST, self.port))
            self.socket.listen(self.__QCON_MAX)

        def spawner():
            print('Use Control-C to exit')
            while True:
                conn, address = self.socket.accept()
                print("Got connection")
                process = multiprocessing.Process(
                    target=self.conn_delegate, args=(conn, address, self.profile_path,
                        self.queue, self.conn_logconf))
                process.daemon = True
                process.start()
                print("Started process %r", process)

        def shutdown():
            print("Shutting down")
            for process in multiprocessing.active_children():
                print("Shutting down process %r", process)
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

    def conn_delegate(self, conn, addr, profile_path, queue, configurer):
        '''deals with an active connection'''

        configurer(queue)
        name = multiprocessing.current_process().name
        logger = logging.getLogger(name)

        def read_socket(s):
            d = conn.recv(s)
            if d == b'':
                raise RuntimeError("socket connection broken")

        read_header = lambda : read_socket(Frame.FRAME_HEADER_LENGTH)
        read_body = lambda hs: read_socket(hs)

        mon = Monitor(logger, conn, factory)
        try:
            logger.debug("Connected %r at %r", conn, addr)
            while True:
                mon.receive(Action(read_body(Frame.decode_header(read_header()))))
        except (RuntimeError, FrameError) as e:
            logger.exception(e)
        except:
            logger.exception("Problem handling request")
        finally:
            logger.debug("Closing socket")
            conn.close()

    def conn_logconf(self):
        pass
