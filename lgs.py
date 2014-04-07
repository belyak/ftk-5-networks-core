#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys as here_sys
import os
import re

VERSION = 0.01
HELLO_MSG = 'Text frequency analysis server v.%s ready.\n\r' % VERSION

import commands_definitions as CMD

LETTERS = u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'\
          u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'\
          u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
          u'abcdefghijklmnopqrstuvwxyz'


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
        line = []
        while True:
            c = os.read(here_sys.stdin.fileno(), 1)
            line.append(c)
            if '\n\r'.find(c) != -1:
                if not self.delimiter_found:
                    if self.delimiter is None:
                        self.delimiter = c
                    elif len(self.delimiter):
                        if self.delimiter != c:
                            self.delimiter = [self.delimiter, c]
                        self.delimiter = ''.join(self.delimiter)
                        self.delimiter_found = True

                return ''.join(line)


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


def clear_buffer():
    GD.collected_lines = []
    message = 'collected lines has been dropped.'
    return message


@command(keyword=CMD.PUT_LINE)
def put_line():
    GD.collected_lines.append(io_stream.read())
    message = 'line has been collected (%d at the moment).' % len(GD.collected_lines)
    return message


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

    message = 'Calculated (%d lines, %d words)' % (len(GD.collected_lines), words_count)
    return message


def print_stats():
    lines = []
    for i, v in GD.GLOBAL_DATA['current'].items():
        lines.append('%s\t%d' % (i, v))
    return '\n'.join(lines)


@command(CMD.EXIT)
def close_session():
    """
exit: closes current session
    """
    return 'OK. Good bye!'

@command(CMD.IPYTHON)
def ipython():
    try:
        from IPython import embed
        embed()
        return ''
    except ImportError:
        return 'ERR: You need to install ipython to run this command!'

COMMANDS += [
    (CMD.CLEAR_BUFFER, clear_buffer),
    #(CMD.PUT_LINE, put_line),
    (CMD.CALC, calc),
    (CMD.PRINT_STATS, print_stats),
    ('ver', lambda: (str(VERSION)))
]

COMMANDS = tuple(COMMANDS)

if __name__ == '__main__':
    io_stream.write(HELLO_MSG)
    cmd = True
    while cmd != CMD.EXIT:
        line = io_stream.read()
        for cmd, callback, in COMMANDS:
            if line.find(cmd) == 0:
                if line.find('??') == len(cmd):
                    cmd = None
                    msg = callback.__doc__ if callback.__doc__ is not None else 'ERR: no documentation'
                    cleaned_msg = (''.join([l.strip() for l in msg.split('\n') if len(l.strip())>4]))
                    io_stream.write(msg)
                    io_stream.write('OK')
                else:
                    msg = callback()
                    io_stream.write(msg)
                    break


