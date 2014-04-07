###
### Вспомогательные функции для преобразования данных
###


def create_message(code, message):
    """
    Формирует однострочный либо многострочный ответ подобно ответу ftp сервера
    :param code: код
    :type code: int
    :param message: текст сообщения
    :type message: str

    :rtype: str
    >>> create_message(200, "Status OK.")
    '200 Status OK.'
    """
    one_line = '\n' not in message

    if one_line:
        return '%d %s' % (code, message)

    lines = message.split('\n')

    first_line = lines[0]
    last_line = lines[-1]

    processed_first_line = '%d-%s' % (code, first_line)
    processed_last_line = '%d %s' % (code, last_line)

    lines[0] = processed_first_line
    lines[-1] = processed_last_line

    return '\n'.join(lines)