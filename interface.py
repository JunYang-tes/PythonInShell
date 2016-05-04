import sys, argparse
from multiprocessing.connection import Client

parser = argparse.ArgumentParser()
parser.add_argument('--indent', help='Is there indent in cold,if no indent this program will try parse indent by {}',
                    action='store_true')
args = vars(parser.parse_args())


def parseline(line):
    if args["indent"]:
        return line
    else:
        return add_indent(line)


def add_indent():
    pass


if __name__ == '__main__':
    if len(sys.argv) == 0:
        print "Usage:interface <file>"
    else:
        conn = Client(address=sys.argv[0], family='AF_UNIX')
        while True:
            try:
                conn.send(parseline(raw_input()))
            except:
                break
