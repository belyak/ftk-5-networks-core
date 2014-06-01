from converters.definitions import MODE_PLAIN, CONVERTER_BY_MODE


class BaseIoAdapter():

    _lines_delimiter = '\r\n'

    def __init__(self):
        self._binary_lines_delimiter = self._lines_delimiter.encode()
        self.delimiter_slice_start = -len(self._binary_lines_delimiter)

    def write(self, data, mode=MODE_PLAIN):
        """
        Записывает в поток данные и сбрасывает буфер.

        :type data: bytes
        """
        full_data = data + self._binary_lines_delimiter
        converter = CONVERTER_BY_MODE[mode]
        """:type: AbstractConverter"""
        encoded_data = converter.encode(full_data)
        return self._write(encoded_data)

    def _write(self, data):
        """
        :param bytes data: данные для отправки клиенту
        """
        raise NotImplementedError()

    def read(self, mode=MODE_PLAIN):
        """
        считывает данные из буфера ввода/вывода до повления символа переноса строки,
        затем возвращает последовательность байт, исключая перенос строки.
        :rtype: bytes
        """
        collected_bytes = b''

        converter = CONVERTER_BY_MODE[mode]
        """:type: AbstractConverter"""

        while collected_bytes[self.delimiter_slice_start:] != self._binary_lines_delimiter:
            message_part = b''
            for _ in range(converter.ENCODED_CHUNK_LEN):
                in_byte = yield self._read_byte
                message_part += in_byte

            collected_bytes += converter.decode(message_part)

        return collected_bytes

    def close(self):
        """
        Закрытие объекта ввода / вывода.
        """
        raise NotImplementedError

    def _read_byte(self):
        """
        Считывает один байт из буфера входящих данных
        """
        raise NotImplementedError

    @property
    def descriptor(self):
        """
        :rtype: int
        """
        raise NotImplementedError