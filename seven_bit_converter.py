def iterate_as_bits(in_bytes):
    """
    итерирует через последовательность байт подавая на выход биты как десятичные 0 или 1
    >>> list(iterate_as_bits(bytes([17])))
    [0, 0, 0, 1, 0, 0, 0, 1]
    >>> list(iterate_as_bits(bytes([255, 48])))
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0]
    """
    for in_byte in in_bytes:
        for weight in [7, 6, 5, 4, 3, 2, 1, 0]:
            yield (in_byte >> weight) & 1

class SevenBitConverter():
    """
    Класс, преобразующий нормальный поток сервера в кодировку 7BM и обратно.
    """
    def encode(self, normal_message):
        """
        :param bytes normal_message: сообщение которое требуется перекодировать в последовательность 7BM
        """
        result = b''
        entry = b'0'  # начало закодированного в 7 бит байта
        return normal_message

    def decode(self, seven_bit_message):
        """
        :param bytes seven_bit_message: закодированное сообщение, которое требуется декодировать.
        """
        return seven_bit_message
