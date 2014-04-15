from constants import CODE_OK, MSG_PL_LINE_HAS_BEEN_COLLECTED, MSG_PT_TEXT_HAS_BEEN_COLLECTED, \
    MSG_CALCULATED_LINES_WORDS, MSG_STATISTICS_HAS_BEEN_LOADED, CODE_NOT_FOUND, ERR_STATISTICS_NOT_FOUND, \
    MSG_STATISTICS_HAS_BEEN_SAVED, ERR_ENCODING_NOT_FOUND, VERSION
from utils import create_message
import commands_definitions as commands

# список, в котором после импорта этого модуля будут все коданды и их обработчики
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


def command(keyword=None, multi_line=False):
    """
    Декоратор, регистрирует функцию в качетве обработчика команды.
    :param keyword: команда
    :type keyword: str
    """
    if keyword is None:
        return lambda a: a

    def wrapper(fn):
        COMMANDS.append((keyword, fn))
        setattr(fn, 'multi_line', multi_line)
        return fn

    return wrapper


class StatefulCommand():
    """
    Команда требующая многострочного ввода и сохраняющая состояние
    """

    def process_line(self, line):
        """
        Обработка одной строки входных данных.
        :returns: требуется повторный вызов process_line со следующей строкой или нет
        :rtype: bool
        """
        raise NotImplementedError

    def get_message(self):
        """
        Получение ответа команды по завершении обработки
        """
        raise NotImplementedError


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


@command(keyword=commands.PUT_TEXT, multi_line=True)
class PutText(StatefulCommand):

    def __init__(self):
        self._lines_collected = 0
        self._separator = None

    def process_line(self, line):

        if self._lines_collected == 0:
            self._separator = line
            self._append_line(line)
            return True
        else:
            separator_position = line.find(self._separator)
            if separator_position != -1:
                self._append_line(line[:separator_position])
                return False
            else:
                self._append_line(line)
                return True

    def get_message(self):
        msg = MSG_PT_TEXT_HAS_BEEN_COLLECTED % (self._lines_collected, GD.statistics.lines_count)
        return create_message(CODE_OK, msg)

    def _append_line(self, line):
        """
        :type line: bytes
        """
        GD.statistics.put_line(line.decode(GD.current_encoding))
        self._lines_collected += 1


###
### Команды расчета и получения статистики
###


@command(keyword=commands.CALC)
def calc(*args, **kwargs):
    GD.statistics.calc()
    msg = MSG_CALCULATED_LINES_WORDS % (GD.statistics.lines_count, GD.statistics.words_count)
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
        raise NotImplementedError('False Statistics.save() result handling is not implemented yet!')

    return create_message(code, msg)


###
### Служебные команды - завершение сеанса, получение версии сервера, установка кодировки текста.
###


@command(keyword=commands.ENCODING)
def set_encoding(line_without_command, *args, **kwargs):
    encoding_name = line_without_command.decode()
    try:
        b'ABC'.decode(encoding=encoding_name)
    except LookupError:
        return create_message(CODE_NOT_FOUND, ERR_ENCODING_NOT_FOUND)

    GD.current_encoding = encoding_name

    return create_message(CODE_OK, 'Encoding has been set to "%s' % encoding_name)


@command(commands.EXIT)
def close_session(*args, **kwargs):
    return create_message(CODE_OK, 'OK. Good bye!')


@command(commands.VERSION)
def get_version(*args, **kwargs):
    return create_message(CODE_OK, str(VERSION))