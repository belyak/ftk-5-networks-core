from collections import Callable
import commands
import commands_definitions
from constants import HELLO_MSG, CODE_BAD_DATA, ERR_COMMAND_NOT_RECOGNIZED
from io_adapter import ConsoleIOAdapter, SocketAdapter
from persistent_statistics import FilePersistentStatistics
from statistics import Statistics
from utils import create_message


def user_session(io_adapter):
    """
    :type io_adapter: BaseIoAdapter
    """
    # начало сессии, выведем приветстие
    io_adapter.write(HELLO_MSG)

    cmd = None

    while cmd != commands_definitions.EXIT:
        # читаем одну строку из входящих данных:
        line = yield from io_adapter.read()
        # перебираем все зарегистрированные команды:
        for cmd, callback, in commands.COMMANDS:
            bin_cmd = cmd.encode()
            cmd_len = len(bin_cmd)
            if line[:cmd_len] == bin_cmd:
                message = callback(line_without_command=line[cmd_len + 1:io_adapter.delimiter_slice_start])
                io_adapter.write(message)
                break
        else:
            # 'это условие выполниться только если цикл завершится нормально, т.е. без break
            message = create_message(CODE_BAD_DATA, ERR_COMMAND_NOT_RECOGNIZED)
            io_adapter.write(message)

    io_adapter.close()


class ClientConnectionContext():
    def __init__(self, io_stream):
        """
        :type io_stream: io_adapter.BaseIOStream
        """
        statistics_name = 'current-%d' % io_stream.descriptor
        self.statistics = Statistics(storage=FilePersistentStatistics(name=statistics_name))
        self.encoding = 'utf-8'
        self.incoming_data = None

        # создадим сопрограмму и запустим; генератор выйдет и вернет ссылку на блокирующий вызов, который мы сохраним,
        # чтобы когда в сокете будут входящие клиентские данные, выполнить его.
        self.session_coroutine = user_session(io_stream)
        self.io_callable = self.session_coroutine.send(self.incoming_data)


class GlobalData:
    count = 0
    current_encoding = 'utf-8'
    statistics = Statistics(storage=FilePersistentStatistics(name='current'))

    @classmethod
    def create(cls, io_stream):
        return ClientConnectionContext(io_stream)

GD = GlobalData


def xinetd_io_loop():
    """
    Цикл взаимодейстивия с пользователем в режиме xinetd сервиса
    """
    io_stream = ConsoleIOAdapter()
    running_user_session = user_session(io_stream)
    try:
        data = None
        while True:
            blocking_read_callback = running_user_session.send(data)
            data = blocking_read_callback()
    except StopIteration:
        running_user_session.close()


def standalone_io_loop():
    """
    Цикл взаимоействия с пользователем в режиме серверного сокета.
    """
    # TODO: использовать неблокирующее чтение из множества сокетов
    import select
    SocketAdapter.initialize_server_socket()

    # noinspection PyProtectedMember
    server_socket = SocketAdapter._server_socket
    server_socket_descriptor = server_socket.fileno()

    sockets_pool = [server_socket.fileno()]
    user_sessions_data = {}

    while True:
        r_list, w_list, e_list = select.select(sockets_pool, [], sockets_pool, 0)

        if server_socket_descriptor in r_list:
            # серверный слушающий сокет появляется как готовый к чтению если можно принять соединение
            new_io_stream = SocketAdapter.accept_connection_and_get_io_adapter()
            fd = new_io_stream.descriptor
            sockets_pool.append(fd)
            user_sessions_data[fd] = GD.create(io_stream=new_io_stream)

        r_clients_list = (d for d in r_list if d != server_socket_descriptor)
        for descriptor in r_clients_list:
            connection_context = user_sessions_data[descriptor]
            """:type: ClientConnectionContext"""

            commands.GD.set_context(connection_context)

            session_coroutine = connection_context.session_coroutine
            try:
                # продолжим (или начнем) выполнение генератора (сопрограммы) отправив в него ранее сохраненные данные
                blocking_read_callback = connection_context.io_callable
                assert isinstance(blocking_read_callback, Callable)
                # на момент необходимости получения генератором новых данных он вернет нам обратный вызов к сокету
                # данные полученные из сокета сохраним в контексте.
                incoming_data = blocking_read_callback()
                connection_context.io_callable = session_coroutine.send(incoming_data)
            except StopIteration:
                session_coroutine.close()
                user_sessions_data.pop(descriptor)
                sockets_pool.remove(descriptor)


if __name__ == '__main__':

    MODE_XINET = 'xinet'
    MODE_STANDALONE = 'standalone'

    # mode = MODE_XINET
    mode = MODE_STANDALONE

    if mode == MODE_XINET:
        # режим работы под управлением xinetd - ioloop запускается один раз с консольным вводом/выводом
        xinetd_io_loop()

    elif mode == MODE_STANDALONE:
        standalone_io_loop()