import os
import sys
from io_adapter.base import BaseIoAdapter


class ConsoleIOAdapter(BaseIoAdapter):
    """
    Адаптер ввода-вывода
    использует stdin / stdout
    """
    def __init__(self):
        super().__init__()

    def _read_byte(self):
        """
        :rtype: bytes
        """
        in_byte = os.read(sys.stdin.fileno(), 1)
        return in_byte

    def _write(self, data):
        """
        :type data: bytes
        """
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

    def close(self):
        pass

    @property
    def descriptor(self):
        return 1