import sys, argparse
from multiprocessing.connection import Client
from threading import Thread

parser = argparse.ArgumentParser()
parser.add_argument('--indent', help='Is there indent in cold,if no indent this program will try parse indent by {}',
                    action='store_true')
parser.add_argument('-t', '--type', help='which type of interface is this,ctrl,code or id', default='ctrl')
parser.add_argument('-a', '--addr', help='Server address', required=True)
args = vars(parser.parse_args())


def main():
    addr = args['addr']
    if args['type'] == 'ctrl':
        ctrl(addr + "_control")
    elif args['type'] == 'code':
        code(addr)
    elif args['type'] == 'io':
        io(addr + "_io")


def get_connection(addr):
    try:
        return Client(address=addr, family='AF_UNIX')
    except:
        # start server
        print 'Server is not ready.You must call pis_init() in your shell script before you can using pis to run python code'
        exit(1)


def ctrl(addr):
    conn = get_connection(addr)

    def read():
        while not conn.recv().startswith("end"):
            pass
        exit(0)

    thread = Thread(target=read)
    thread.setDaemon(True)
    thread.start()
    while True:
        try:
            conn.send(raw_input())
        except:
            break
    thread.join()


def code(addr):
    conn = get_connection(addr)
    while True:
        try:
            conn.send(parseline(raw_input()))
        except:
            break


def io(addr):
    conn = get_connection(addr)
    while True:
        msg = conn.recv()
        if msg.startwiths("read"):
            conn.send(raw_input())
        elif msg.startwiths("write"):
            sys.stdout.write(msg[6:])
        else:
            break


def parseline(line):
    if args["indent"]:
        return line
    else:
        return add_indent(line)


indent = 0


def add_indent(line):
    global indent
    IN_STR = 1
    OUT_STR = 0
    state = 0
    ret = []
    last_char = line[0]
    for c in line:
        if state == OUT_STR:
            if c == '"' or c == "'":
                state = IN_STR
                ret.append(c)
            elif c == '{':
                indent += 1
                ret.append('\n')
                ret.append(' ' * indent)
            elif c == '}':
                indent -= 1
                ret.append('\n')
                ret.append(' ' * indent)
            elif c == '\n':
                ret.append('\n')
                ret.append(' ' * indent)
            else:
                ret.append(c)
        else:
            ret.append(c)
            if (c == '"' or c == "'") and last_char != '\\':
                state = OUT_STR
        last_char = c
    return "".join(ret)


if __name__ == '__main__':
    main()
