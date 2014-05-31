###
### Вспомогательные функции для преобразования данных
###
from constants import LINES_DELIMITER


def create_message(code, message, as_bytes=True):
    """
    Формирует однострочный либо многострочный ответ подобно ответу ftp сервера
    :param code: код
    :type code: int
    :param message: текст сообщения
    :type message: str

    :rtype: str or bytes
    >>> create_message(200, "Status OK.")
    b'200 Status OK.'
    """
    one_line = LINES_DELIMITER not in message

    if one_line:
        line = '%d %s' % (code, message)
        return line.encode() if as_bytes else line

    lines = message.split(LINES_DELIMITER)

    first_line = lines[0]
    last_line = lines[-1]

    processed_first_line = '%d-%s' % (code, first_line)
    processed_last_line = '%d %s' % (code, last_line)

    lines[0] = processed_first_line
    lines[-1] = processed_last_line

    if as_bytes:
        return (LINES_DELIMITER.join(lines)).encode()
    else:
        return LINES_DELIMITER.join(lines)