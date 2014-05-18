import os
import sys as here_sys
from converters.definitions import MODE_PLAIN, CONVERTER_BY_MODE

from converters.seven_bit_converter import SevenBitConverter


class BaseIoAdapter():

    _lines_delimiter = '\r\n'

    def __init__(self):
        self._binary_lines_delimiter = self._lines_delimiter.encode()
        self.delimiter_slice_start = -len(self._binary_lines_delimiter)

    def set_encoding(self, encoding):
        pass

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


class ConsoleIOAdapter(BaseIoAdapter):
    """
    Адаптер ввода-вывода

    Сейчас реализует консольный побайтный ввод-вывод, в дальнейшем должен быть разделен на два подкласса:
    консольный и сокет ввод/вывод для реализации xinetd и standalone режимов
    """

    _lines_delimiter = '\n'

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
        return os.read(here_sys.stdin.fileno(), 1)

    def write(self, data, mode=MODE_PLAIN):
        """
        :type data: bytes
        """
        here_sys.stdout.write(data.decode(self.__encoding))
        here_sys.stdout.write(self._lines_delimiter)
        here_sys.stdout.flush()

    def close(self):
        pass

import socket

MAX_CONNECTIONS = 10


class SocketAdapter(BaseIoAdapter):
    """
    Класс для получения сообщений из открытого серверного сокета
    """
    _server_socket = None
    """:type: socket.socket"""

    def __init__(self, client_socket):
        """
        :type client_socket: socket.socket
        """
        super().__init__()
        self._client_socket = client_socket

    @classmethod
    def initialize_server_socket(cls):
        """
        :rtype: socket.socket
        """
        cls._server_socket = socket.socket()
        cls._server_socket.setblocking(0)
        hostname, port = socket.gethostname(), 8022
        cls._server_socket.bind((hostname, port))
        print('Bound to %s at %d' % (hostname, port))
        cls._server_socket.listen(MAX_CONNECTIONS)
        return cls._server_socket

    @classmethod
    def accept_connection_and_get_io_adapter(cls):
        """
        Принимает соединение и возвращает объект с интерфейсом BaseIoAdapter осуществляющий обмен данными с сокетом.

        :rtype: BaseIoAdapter
        """
        if cls._server_socket is None:
            cls.initialize_server_socket()

        client_socket, _ = cls._server_socket.accept()
        return SocketAdapter(client_socket)

    @property
    def descriptor(self):
        """
        :rtype: int
        """
        return self._client_socket.fileno()

    def _read_byte(self):
        return self._client_socket.recv(1)

    def _write(self, data):
        """
        :type data: bytes
        """
        self._client_socket.sendall(data)

    def close(self):
        self._client_socket.close()
