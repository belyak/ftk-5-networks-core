from io_adapter import IOAdapter
from persistent_statistics import FilePersistentStatistics
from statistics import Statistics

from utils import create_message
import commands_definitions as commands

VERSION = 0.01
HELLO_MSG = ('Text frequency analysis server v.%s ready.\n\r' % VERSION).encode()

CODE_OK = 200
CODE_NOT_FOUND = 404


class GlobalData:
    current_encoding = 'utf-8'
    statistics = Statistics(storage=FilePersistentStatistics(name='current'))

GD = GlobalData

io_stream = IOAdapter()


COMMANDS = []


def command(keyword=None):
    if keyword is None:
        return lambda a: a

    def wrapper(fn):
        COMMANDS.append((keyword, fn))
        return fn

    return wrapper


###
### Команды работы с буфером текста - добавление строки, текста, очистка
###

@command(keyword=commands.CLEAR_BUFFER)
def clear_buffer(*args, **kwargs):
    GD.statistics.clear_buffer()
    msg = 'collected lines has been dropped.'
    return create_message(CODE_OK, msg)


@command(keyword=commands.PUT_LINE)
def put_line(line_without_command, *args, **kwargs):
    """
    :type line_without_command: bytes
    """
    GD.statistics.put_line(line_without_command.decode(GD.current_encoding))
    msg = 'line has been collected (%d at the moment).' % GD.statistics.lines_count
    return create_message(CODE_OK, msg)


@command(keyword=commands.PUT_TEXT)
def put_text(line_without_command, *args, **kwargs):
    separator = line_without_command
    lines_collected = 0
    last_line = False
    while not last_line:
        in_line = io_stream.read()
        separator_position = in_line.find(separator)
        if separator_position != -1:
            in_line = in_line[:separator_position]
            last_line = True
        GD.statistics.put_line(in_line.decode(GD.current_encoding))
        lines_collected += 1
    msg = '%d lines has been collected (%d total)' % (lines_collected, GD.statistics.lines_count)
    return create_message(CODE_OK, msg)

###
### Команды расчета и получения статистики
###


@command(keyword=commands.CALC)
def calc(*args, **kwargs):
    GD.statistics.calc()
    msg = 'Calculated (%d lines, %d words)' % (GD.statistics.lines_count, GD.statistics.words_count)
    return create_message(CODE_OK, msg)


@command(keyword=commands.PRINT_STATS)
def print_stats(*args, **kwargs):
    lines = ['STATISTICS']
    current_stats = GD.statistics.get()
    """:type: dict"""
    for i, v, in current_stats.items():
        lines.append('%s %d' % (i, v))
    return create_message(CODE_OK, '\n'.join(lines))

###
### Команды сохранения и загрузки статистики
###


@command(keyword=commands.LOAD)
def load_statistics(line_without_command, *args, **kwargs):
    result = GD.statistics.load(name=line_without_command.decode())

    if result:
        code = CODE_OK
        msg = 'Statistics loaded'
    else:
        code = CODE_NOT_FOUND
        msg = 'Statistics not found'

    return create_message(code, msg)


@command(keyword=commands.STORE)
def store_statistics(line_without_command, *args, **kwargs):
    result = GD.statistics.save(name=line_without_command.decode())
    if result:
        code = CODE_OK
        msg = 'Statistics has been saved'
    else:
        raise NotImplementedError('False Statistics.save() result handling is not implemented yet!')

    return create_message(code, msg)


###
### Служебные команды - завершение сеанса и получение версии сервера
###


@command(commands.EXIT)
def close_session(*args, **kwargs):
    return create_message(CODE_OK, 'OK. Good bye!')


@command(commands.VERSION)
def get_version(*args, **kwargs):
    return create_message(CODE_OK, str(VERSION))

if __name__ == '__main__':
    io_stream.write(HELLO_MSG)

    cmd = True

    while cmd != commands.EXIT:
        line = io_stream.read()
        for cmd, callback, in COMMANDS:
            bin_cmd = cmd.encode()
            cmd_len = len(bin_cmd)
            if line[:cmd_len] == bin_cmd:
                message = callback(line_without_command=line[cmd_len + 1:-1])
                io_stream.write(message)
                break