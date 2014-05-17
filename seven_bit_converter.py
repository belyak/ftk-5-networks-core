def iterate_as_bits(in_bytes, with_ix=False):
    """
    итерирует через последовательность байт подавая на выход биты как десятичные 0 или 1
    >>> list(iterate_as_bits(bytes([17])))
    [0, 0, 0, 1, 0, 0, 0, 1]
    >>> list(iterate_as_bits(bytes([255, 48])))
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0]
    """
    weights = [7, 6, 5, 4, 3, 2, 1, 0]
    for in_byte in in_bytes:
        for weight in weights:
            yield (in_byte >> weight) & 1


def significant_bits(in_bits):
    """
    генератор, выдающий только значимые биты кодированной последовательности:
    >>> list(significant_bits([0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1]))
    [1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1]
    """
    for ix, in_bit in enumerate(in_bits):
        if ix % 8 == 0:
            continue
        yield in_bit


class SevenBitConverter():
    """
    Класс, преобразующий нормальный поток сервера в кодировку 7BM и обратно.n
    """

    def __init__(self):
        self.bit_weight = lambda n: 2**n  # вес бита

    def encode(self, normal_message):
        """
        :param bytes normal_message: сообщение которое требуется перекодировать в последовательность 7BM
        """
        result = []
        out_byte = 0

        for ix, in_bit in enumerate(iterate_as_bits(normal_message)):
            bit_position = 6 - (ix % 7)
            out_byte += in_bit * self.bit_weight(bit_position)
            if bit_position == 0:
                result.append(out_byte)
                out_byte = 0

        return bytes(result)

    def decode(self, seven_bit_message):
        """
        :param bytes seven_bit_message: закодированное сообщение, которое требуется декодировать.
        """
        result = []
        out_byte = 0

        for ix, in_bit in enumerate(significant_bits(iterate_as_bits(seven_bit_message))):
            bit_position = 7 - (ix % 8)
            out_byte += in_bit * self.bit_weight(bit_position)
            if bit_position == 0:
                result.append(out_byte)
                out_byte = 0

        return bytes(result)
