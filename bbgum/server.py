from bbgum.frame import Action, Frame, FrameError
from bbgum.monitor import Monitor
from engine.erp import ControllerFactory
from misc.tricks import dump_exception
import logging
import multiprocessing
import socket


class BbGumServer(object):

    __HOST = ''  # Symbolic name meaning all available interfaces
    __QCON_MAX = 5  # Maximum number of queued connections

    def __init__(self, queue, profile_path, port):
        self.queue = queue
        self.profile_path = profile_path
        self.port = port
        self.ps = []

    def start(self, debug):
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
                                                     self.queue, self.conn_logconf, debug))
                process.daemon = True
                process.start()
                self.ps.append(process)
                print("Started process %r", process)

        def shutdown():
            print("Shutting down")
            for p in self.ps:
                if p.is_alive():
                    print("Shutting down process {}".format(repr(p)))
                    p.terminate()
                    p.join()

        try:
            listener()
            spawner()
        except KeyboardInterrupt:
            raise
        except:
            raise
        finally:
            shutdown()

    def conn_delegate(self, conn, addr, profile_path, queue, configurer, debug):
        """deals with an active connection"""

        configurer(queue, debug)
        name = multiprocessing.current_process().name
        logger = logging.getLogger(name)

        def read_socket(s):
            d = conn.recv(s)
            if d == b'':
                raise RuntimeError("socket connection broken")
            return d

        read_header = lambda: read_socket(Frame.FRAME_HEADER_LENGTH)
        read_body = lambda hs: read_socket(hs)

        mon = None
        try:
            factory = ControllerFactory(logger, profile_path)
            mon = Monitor(logger, conn, factory)
        except:
            logger.error("Problem upon initialization of Monitor entity")
            logger.debug("Closing socket")
            logger.error(dump_exception())
            conn.close()
            return

        try:
            logger.debug("Connected %r at %r", conn, addr)
            while True:
                mon.receive(Action(read_body(Frame.decode_header(read_header()))))
        except (RuntimeError, FrameError) as e:
            logger.exception(e)
        except:
            logger.exception("Problem handling request")
            logger.error(dump_exception())
        finally:
            logger.debug("Closing socket")
            conn.close()

    def conn_logconf(self, queue, debug):
        h = logging.handlers.QueueHandler(queue)
        root = logging.getLogger()
        root.addHandler(h)
        root.setLevel(logging.DEBUG if debug else logging.INFO)
