from bbgum.frame import Action, Frame, FrameError
from bbgum.monitor import Monitor
from misc.factory import Factory
from custom.profile import ProfileReader
from misc.tricks import dict_params
import logging
import traceback
import multiprocessing
import socket
import os
import sys


class ControllerFactory(Factory):
    def __init__(self, logger, profile_path):
        super().__init__()
        self.logger = logger
        pt = self.__read_settings(profile_path)
        self.__makeup_factory(pt.bbgum.controllers)

    def __read_settings(self, s_file):
        self.logger.debug("looking for config profile file in:\n{0}".format(
            os.path.abspath(s_file)))
        if os.path.isfile(s_file):
            reader = ProfileReader(self.logger)
            return reader(s_file)
        raise Exception("unable to locate the config profile file")

    def __makeup_factory(self, variants):
        devents = dict_params(
            ProfileReader.get_content(
                variants, ProfileReader.PNODE_MANY),
            'archetype', 'event_mod')
        for archetype, event_mod in devents.items():
            try:
                m = __import__(event_mod)

                if not hasattr(m, "impt_class"):
                    msg = "module {0} has no impt_class attribute".format(event_mod)
                    raise RuntimeError(msg)
                cname = getattr(m, "impt_class")

                if not hasattr(m, cname):
                    msg = "module {0} has no {1} class implemented".format(event_mod, cname)
                    raise RuntimeError(msg)
                ic = getattr(m, cname)
                self.subscribe(int(archetype, 0), ic)
            except (ImportError, RuntimeError) as e:
                self.logger.fatal("{0} support library failure".format(event_mod))
                raise e


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
        '''deals with an active connection'''

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
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(
                exc_type,
                exc_value,
                exc_traceback
            )
            logger.error(''.join('!! ' + line for line in lines))
        finally:
            logger.debug("Closing socket")
            conn.close()

    def conn_logconf(self, queue, debug):
        h = logging.handlers.QueueHandler(queue)
        root = logging.getLogger()
        root.addHandler(h)
        root.setLevel(logging.DEBUG if debug else logging.INFO)
