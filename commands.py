from constants import (CODE_OK, MSG_PL_LINE_HAS_BEEN_COLLECTED,
                       MSG_CALCULATED_LINES_WORDS,
                       MSG_STATISTICS_HAS_BEEN_LOADED, CODE_NOT_FOUND,
                       ERR_STATISTICS_NOT_FOUND, MSG_STATISTICS_HAS_BEEN_SAVED,
                       ERR_ENCODING_NOT_FOUND, VERSION,
                       MSG_STATISTICS_HAS_BEEN_MERGED,
                       MSG_STATISTICS_TO_MERGE_NOT_FOUND)

from converters.definitions import CONVERTER_BY_MODE
from utils import create_message
import commands_definitions as commands

# список, в котором после импорта этого модуля будут собранв все коданды и их
# обработчики
COMMANDS = []


class GD:
    statistics = None
    """:type: Statistics"""
    current_encoding = 'utf-8'

    @classmethod
    def set_context(cls, context):
        """
        :type context: ClientConnectionContext
        """
        cls.current_encoding = context.encoding
        cls.statistics = context.statistics


def command(keyword=None):
    """
    Декоратор, регистрирует функцию в качестве обработчика команды.

    :param keyword: мнемоника команды
    :type keyword: str
    """
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
    msg = MSG_PL_LINE_HAS_BEEN_COLLECTED % GD.statistics.lines_count
    return create_message(CODE_OK, msg)

###
### Команды расчета и получения статистики
###


@command(keyword=commands.CALC)
def calc(*args, **kwargs):
    GD.statistics.calc()
    msg = MSG_CALCULATED_LINES_WORDS % (GD.statistics.lines_count,
                                        GD.statistics.words_count)
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
### Команды сохранения, загрузки и соединения статистики
###


@command(keyword=commands.LOAD)
def load_statistics(line_without_command, *args, **kwargs):
    statistics_name = line_without_command.decode()
    result = GD.statistics.load(name=statistics_name)

    if result:
        code = CODE_OK
        msg = MSG_STATISTICS_HAS_BEEN_LOADED % statistics_name
    else:
        code = CODE_NOT_FOUND
        msg = ERR_STATISTICS_NOT_FOUND % statistics_name

    return create_message(code, msg)


@command(keyword=commands.STORE)
def store_statistics(line_without_command, *args, **kwargs):
    statistics_name = line_without_command.decode()
    result = GD.statistics.save(name=statistics_name)
    if result:
        code = CODE_OK
        msg = MSG_STATISTICS_HAS_BEEN_SAVED % statistics_name
    else:
        msg = 'False Statistics.save() result handling is not implemented yet!'
        raise NotImplementedError(msg)

    return create_message(code, msg)

@command(keyword=commands.MERGE)
def merge_statistics(line_without_command, *args, **kwargs):
    statistics_to_merge_with = line_without_command.decode()
    result = GD.statistics.merge(name=statistics_to_merge_with)
    if result:
        code = CODE_OK
        msg = MSG_STATISTICS_HAS_BEEN_MERGED % statistics_to_merge_with
    else:
        code = CODE_NOT_FOUND
        msg = MSG_STATISTICS_TO_MERGE_NOT_FOUND % statistics_to_merge_with

    return create_message(code, msg)

###
### Служебные команды - завершение сеанса, получение версии сервера
###


@command(keyword=commands.ENCODING)
def set_encoding(line_without_command, *args, **kwargs):
    encoding_name = line_without_command.decode()
    try:
        b'ABC'.decode(encoding=encoding_name)
    except LookupError:
        return create_message(CODE_NOT_FOUND, ERR_ENCODING_NOT_FOUND)

    GD.current_encoding = encoding_name

    return create_message(CODE_OK,
                          'Encoding has been set to "%s' % encoding_name)


@command(keyword=commands.MODE)
def set_mode(line_without_command, transfer_mode, *args, **kwargs):
    """
    :type transfer_mode: TransferMode
    """
    mode = line_without_command.decode()
    if mode in CONVERTER_BY_MODE.keys():
        transfer_mode.mode = mode
    else:
        return create_message(400, 'Mode `%s` is not supported!' % mode)

    return create_message(200, 'Mode has been set to `%s`' % mode)

@command(commands.EXIT)
def close_session(*args, **kwargs):
    return create_message(CODE_OK, 'OK. Good bye!')


@command(commands.VERSION)
def get_version(*args, **kwargs):
    return create_message(CODE_OK, str(VERSION))