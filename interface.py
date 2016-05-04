import sys
from multiprocessing.connection import Client

if __name__ == '__main__':
    if len(sys.argv) == 0:
        print "Usage:interface <file>"
    else:
        conn = Client(address=sys.argv[0], family='AF_UNIX')
        while True:
            try:
                conn.send(raw_input())
            except:
                break
