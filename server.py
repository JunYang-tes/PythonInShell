import sys, os, Queue
from threading import Semaphore, Thread, Event
from multiprocessing.connection import Listener


class OutStream:
    def __init__(self):
        self.buff = Queue.Queue()

    def write(self, string):
        self.buff.put(string)

    def writelines(self, lines):
        for line in lines:
            self.buff.put(line)

    def isattry(self):
        return False

    def flush(self):
        pass

    def get(self):
        return self.buff.get()


class InStream:
    def __init__(self):
        self.buf = Queue.Queue()
        self.encoding = u'UTF8'
        self.need_input = Semaphore(0)

    def isatty(self):
        return False

    def readline(self):
        if self.buf.empty():
            # if there is no line in buf,raise an event to notify client input
            self.need_input.release()
        # self.buf is a blocking queue
        return self.buf.get()

    def put(self, string):
        self.buf.put(string)

    def wait(self):
        self.need_input.acquire()

    def readlines(self):
        pass


class Server:
    """
    Read code & cmd from client and execute codes in this
    python interpreter
    """

    def __init__(self, address):
        self._address = address
        self.code_lines = []
        # code_channel used to receive code line
        self.code_channel = None
        # control_channel used to send & receive control msg
        self.control_channel = None
        # read & write
        self.io_channel = None
        self.quit = Event()
        self.runging = False
        sys.stdin = self._in = InStream()
        sys.stdout = self._out = OutStream()

    def read(self):
        while not self.quit.isSet():
            self._in.wait()
            # tell client need input
            self.io_channel.send('read')

    def write(self):
        while not self.quit.isSet():
            # because of _out has a blocking buf,don't worry
            string = self._out.get()
            self.io_channel.send('write ' + string)

    def listen_code(self):
        listener = Listener(address=self._address, family='AF_UNIX')
        while not self.quit.isSet():
            self.code_channel = listener.accept()
            while not self.quit.isSet():
                try:
                    msg = self.code_channel.recv()
                    self.code_lines.append(msg)
                except EOFError:
                    # client exited but it may be started again
                    continue

    def listen_io(self):
        listener = Listener(address=self._address + "_io", family='AF_UNIX')
        while not self.quit.isSet():
            self.io_channel = listener.accept()

    def start(self):
        if os.path.exists(self._address):
            os.remove(self._address)

        # start input & output thread
        rdt = Thread(target=self.read)
        rdt.setName('[read]')
        rdt.setDaemon(True)
        rdt.start()
        wrt = Thread(target=self.write)
        wrt.setName('[write]')
        wrt.setDaemon(True)
        wrt.start()
        # code receive thread
        codet = Thread(target=self.listen_code)
        codet.setName('[code-recv]')
        codet.setDaemon(True)
        codet.start()

        # One server only accept one connection
        # control channel run in main thread
        ctrl_listener = Listener(address=self._address + "_control", family='AF_UNIX')
        while not self.quit.isSet():
            self.control_channel = ctrl_listener.accept()
            while not self.quit.isSet():
                try:
                    msg = self.control_channel.recv()
                    if msg.startswith('cmd'):
                        # TODO more powerfull cmd process
                        cmd = msg[4:]
                        if cmd.startswith("exe"):
                            # TODO execute python codes
                            exec ("\n".join(self.code_lines))
                            self.control_channel.send('end')
                            self.io_channel.send('end')
                            self.code_lines = []
                        elif cmd.startswith("quit"):
                            self.quit.set()
                except EOFError:
                    continue


if __name__ == '__main__':
    if len(sys.argv) > 0:
        Server(sys.argv[0]).start()
    else:
        Server('/tmp/PythonInShell').start()
