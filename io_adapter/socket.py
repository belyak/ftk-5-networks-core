import socket
from io_adapter.base import BaseIoAdapter


class SocketAdapter(BaseIoAdapter):
    """
    Адаптер ввода вывод использующий TCP socket
    """
    _server_socket = None
    """:type: socket.socket"""

    MAX_CONNECTIONS = 10

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
        hostname, port = socket.gethostname(), 8023
        while True:
            try:
                cls._server_socket.bind((hostname, port))
                break
            except OSError:
                port += 1
        print('Bound to %s at %d' % (hostname, port))
        cls._server_socket.listen(cls.MAX_CONNECTIONS)
        return cls._server_socket

    @classmethod
    def accept_connection_and_get_io_adapter(cls):
        """
        Принимает соединение и возвращает объект с интерфейсом BaseIoAdapter осуществляющий обмен данными с сокетом.

        :rtype: io_adapter.base.BaseIoAdapter
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