import sys, os
from multiprocessing.connection import Listener


class Server:
    """
    Read code & cmd from client and execute codes in this
    python interpreter
    """

    def __init__(self, address):
        self._address = address
        self.code_lines = []

    def start(self):
        if os.path.exists(self._address):
            os.remove(self._address)
        listener = Listener(address=self._address, family='AF_UNIX')
        # One server only accept one connection
        conn = listener.accept()
        while True:
            try:
                msg = conn.recv()
                if msg.startswith('cmd'):
                    # TODO more powerfull cmd process
                    cmd = msg[4:]
                    if cmd.startswith("exe"):
                        # TODO execute python codes
                        exec ("\n".join(self.code_lines))
                        self.code_lines = []
                    elif cmd.startswith("quit"):
                        return
                else:
                    self.code_lines.append(msg)
            except EOFError:
                exec ("\n".join(self.code_lines))
                self.code_lines=[]


if __name__ == '__main__':
    if len(sys.argv) > 0:
        Server(sys.argv[0]).start()
    else:
        Server('/tmp/PythonInShell').start()
