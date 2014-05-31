import os
import sys
from converters.definitions import MODE_PLAIN
from io_adapter.base import BaseIoAdapter


class ConsoleIOAdapter(BaseIoAdapter):
    """
    Адаптер ввода-вывода
    использует stdin / stdout

    """

    def __init__(self):
        super().__init__()
        self.__encoding = 'utf-8'

    def set_encoding(self, encoding):
        """
        Устанавливает кодировку вывода в поток.
        Вызов влияет только на консольный режим работы приложения.
        """
        self.__encoding = encoding

    def _read_byte(self):
        """
        :rtype: bytes
        """
        in_byte = os.read(sys.stdin.fileno(), 1)
        return in_byte

    def write(self, data, mode=MODE_PLAIN):
        """
        :type data: bytes
        """
        sys.stdout.write(data.decode(self.__encoding))
        sys.stdout.write(self._lines_delimiter)
        sys.stdout.flush()

    def close(self):
        pass

    @property
    def descriptor(self):
        return 1