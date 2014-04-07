###
### Вспомогательные функции для преобразования данных
###


def create_message(code, message):
    """
    >>> create_message(200, "Status OK.")
    '200 Status OK.'
    """
    one_line = '\n' not in message

    if one_line:
        return '%d %s' % (code, message)

    raise NotImplementedError('Multi lines processing is not implemented yet!')