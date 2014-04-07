import sys as here_sys
import os

from utils import create_message
import commands_definitions as commands

VERSION = 0.01
HELLO_MSG = 'Text frequency analysis server v.%s ready.\n\r' % VERSION

CODE_OK = 200

LETTERS = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'\
          'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'\
          'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
          'abcdefghijklmnopqrstuvwxyz'


CURRENT = 'current'


class GlobalData:
    GLOBAL_DATA = {
        CURRENT: {}
    }
    collected_lines = []
    current_encoding = 'utf-8'

GD = GlobalData


class IOAdapter():
    def __init__(self):
        self.delimiter = None
        self.delimiter_found = False

    def read(self):
        lines = []
        while True:
            c = os.read(here_sys.stdin.fileno(), 1).decode()
            lines.append(c)
            if '\n\r'.find(c) != -1:
                if not self.delimiter_found:
                    if self.delimiter is None:
                        self.delimiter = c
                    elif len(self.delimiter):
                        if self.delimiter != c:
                            self.delimiter = [self.delimiter, c]
                        self.delimiter = ''.join(self.delimiter)
                        self.delimiter_found = True

                return ''.join(lines)

    def write(self, data, line_break=True):
        here_sys.stdout.write(data)
        if line_break and self.delimiter is not None:
            here_sys.stdout.write(self.delimiter)
        here_sys.stdout.flush()

io_stream = IOAdapter()


COMMANDS = []


def command(keyword=None):
    if keyword is None:
        return lambda a: a

    def wrapper(fn):
        COMMANDS.append((keyword, fn))
        return fn

    return wrapper


@command(keyword=commands.CLEAR_BUFFER)
def clear_buffer():
    GD.collected_lines = []
    msg = 'collected lines has been dropped.'
    return create_message(CODE_OK, msg)


@command(keyword=commands.PUT_LINE)
def put_line():
    GD.collected_lines.append(io_stream.read())
    msg = 'line has been collected (%d at the moment).' % len(GD.collected_lines)
    return create_message(CODE_OK, msg)


@command(keyword=commands.CALC)
def calc():
    data = GD.GLOBAL_DATA['current']
    words_count = 0
    for l in GD.collected_lines:
        words = l.decode(GD.current_encoding).split()
        for w in [w.upper() for w in words]:
            if w in data.keys():
                data[w] += 1
            else:
                data[w] = 1
        words_count += len(words)

    msg = 'Calculated (%d lines, %d words)' % (len(GD.collected_lines), words_count)
    return create_message(CODE_OK, msg)


@command(keyword=commands.PRINT_STATS)
def print_stats():
    lines = []
    for i, v, in GD.GLOBAL_DATA['current'].items():
        lines.append('%s\t%d' % (i, v))
    return '\n'.join(lines)


@command(commands.EXIT)
def close_session():
    """
    exit: closes current session
    """
    return 'OK. Good bye!'


COMMANDS += [
    ('ver', lambda: (str(VERSION)))
]

if __name__ == '__main__':
    io_stream.write(HELLO_MSG)

    cmd = True

    while cmd != commands.EXIT:
        line = io_stream.read()
        for cmd, callback, in COMMANDS:
            if line.find(cmd) == 0:
                if line.find('??') == len(cmd):
                    cmd = None
                    message = callback.__doc__ if callback.__doc__ is not None else 'ERR: no documentation'
                    cleaned_msg = (''.join([l.strip() for l in message.split('\n') if len(l.strip()) > 4]))
                    io_stream.write(message)
                    io_stream.write('OK')
                else:
                    message = callback()
                    io_stream.write(message)
                    break