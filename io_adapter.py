import os
import sys as here_sys


class IOAdapter():
    """
    Адаптер ввода-вывода

    Сейчас реализует консольный побайтный ввод-вывод, в дальнейшем должен быть разделен на два подкласса:
    консольный и сокет ввод/вывод для реализации xinetd и standalone режимов
    """
    def __init__(self):
        self.__possible_delimiters = '\n\r'.encode()
        self.__encoding = 'utf-8'
        self.delimiter = None
        self.delimiter_found = False

    def set_encoding(self, encoding):
        """
        Устанавливает кодировку вывода в поток.
        Вызов влияет только на консольный режим работы приложения.
        """
        self.__encoding = encoding

    def read(self):
        """
        считывает данные из буфеа ввода/вывода до повления символа переноса строки,
        затем возвращает последовательность байт, исключая перенос строки.
        :rtype: bytes
        """
        collected_bytes = b''
        while True:
            in_byte = os.read(here_sys.stdin.fileno(), 1)
            collected_bytes += in_byte
            if in_byte in self.__possible_delimiters:
                if not self.delimiter_found:
                    if self.delimiter is None:
                        self.delimiter = in_byte
                    elif len(self.delimiter):
                        if self.delimiter != in_byte:
                            self.delimiter = self.delimiter + in_byte
                        self.delimiter_found = True
                return collected_bytes

    def write(self, data, line_break=True):
        """
        :type data: bytes
        :type line_break: bool
        """
        here_sys.stdout.write(data.decode(self.__encoding))
        if line_break and self.delimiter is not None:
            here_sys.stdout.write(self.delimiter.decode(self.__encoding))
        here_sys.stdout.flush()