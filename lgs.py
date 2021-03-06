from collections import Callable
from optparse import OptionParser
import select

from banner_message import BannerMessage
import commands
import commands_definitions
from constants import CODE_BAD_DATA, ERR_COMMAND_NOT_RECOGNIZED
from converters.transfer_mode import TransferMode
from io_adapter.console import ConsoleIOAdapter
from io_adapter.socket import SocketAdapter
from persistent_statistics import FilePersistentStatistics
from statistics import Statistics
from utils import create_message


def user_session(io_adapter):
    """
    Класс, реализующий логику работы с конкретным подключенным к серверу
    пользователем. При запуске выводит пользователю приветственное сообщение,
    затем в распознает команды получаемые от клиента и выполняет их, после
    выполнения команды exit завершает работу.

    :type io_adapter: BaseIoAdapter
    """
    # начало сессии, выведем приветстие
    io_adapter.write(create_message(200, BannerMessage.get()))

    cmd = None

    transfer_mode = TransferMode()

    while cmd != commands_definitions.EXIT:
        # читаем одну строку из входящих данных:
        line = yield from io_adapter.read(transfer_mode.mode)
        """:type: bytes"""
        # перебираем все зарегистрированные команды:
        for cmd, callback, in commands.COMMANDS:
            bin_cmd = cmd.encode()
            cmd_len = len(bin_cmd)
            if line[:cmd_len] == bin_cmd:
                lwc = line[cmd_len + 1:io_adapter.delimiter_slice_start].rstrip(b' ')
                callback_kwargs = {
                    'line_without_command': lwc,
                    'transfer_mode': transfer_mode,
                }
                message = callback(**callback_kwargs)
                io_adapter.write(message, transfer_mode.mode)
                break
        else:
            # это условие выполниться только если цикл завершится нормально,
            # т.е. без break
            message = create_message(CODE_BAD_DATA, ERR_COMMAND_NOT_RECOGNIZED)
            io_adapter.write(message, transfer_mode.mode)

    io_adapter.close()


class ClientConnectionContext():
    """
    Класс-обертка для данных конкретной пользовательской сессии.
    Используется для сохранения контекста при переключении сессий в standalone
    режиме.
    """
    def __init__(self, io_stream):
        """
        :type io_stream: io_adapter.BaseIOStream
        """
        statistics_name = 'current-%d' % io_stream.descriptor
        self.statistics = Statistics(
            storage=FilePersistentStatistics(name=statistics_name)
        )
        self.encoding = 'utf-8'
        self.incoming_data = None

        # создадим сопрограмму и запустим; генератор выйдет и вернет ссылку на
        # блокирующий вызов, который мы сохраним, чтобы когда в сокете будут
        # входящие клиентские данные, выполнить его.
        self.session_coroutine = user_session(io_stream)
        self.io_callable = self.session_coroutine.send(self.incoming_data)
        """:type: collections.Callable"""


def xinetd_io_loop():
    """
    Цикл взаимодейстивия с пользователем в режиме xinetd сервиса
    """
    io_stream = ConsoleIOAdapter()
    single_context = ClientConnectionContext(io_stream=io_stream)
    running_user_session = single_context.session_coroutine
    commands.GD.set_context(single_context)
    try:
        data = single_context.io_callable()

        while True:
            blocking_read_callback = running_user_session.send(data)
            """:type: collections.Callable"""
            data = blocking_read_callback()
    except StopIteration:
        running_user_session.close()


def standalone_io_loop():
    """
    Цикл взаимодействия с пользователем в режиме серверного сокета.
    """
    SocketAdapter.initialize_server_socket()

    # noinspection PyProtectedMember
    server_socket = SocketAdapter._server_socket
    server_socket_descriptor = server_socket.fileno()

    sockets_pool = []
    user_sessions_data = {}

    while True:
        r_list, w_list, e_list = select.select(
            sockets_pool + [server_socket_descriptor],
            [],
            sockets_pool + [server_socket_descriptor],
            0)

        if server_socket_descriptor in r_list:
            # серверный слушающий сокет появляется как готовый к чтению если
            # можно принять соединение
            new_io_stream = SocketAdapter.accept_connection_and_get_io_adapter()
            fd = new_io_stream.descriptor
            sockets_pool.append(fd)
            user_sessions_data[fd] = ClientConnectionContext(io_stream=new_io_stream)
            print('Incoming connection. Currently %d %s' % (len(sockets_pool),
                                                            sockets_pool))

        r_clients_list = (d for d in r_list if d != server_socket_descriptor)
        for descriptor in r_clients_list:
            connection_context = user_sessions_data[descriptor]
            """:type: ClientConnectionContext"""

            commands.GD.set_context(connection_context)

            session_coroutine = connection_context.session_coroutine
            try:
                # продолжим (или начнем) выполнение генератора (сопрограммы)
                # отправив в него ранее сохраненные данные
                blocking_read_callback = connection_context.io_callable
                assert isinstance(blocking_read_callback, Callable)

                # на момент необходимости получения генератором новых данных
                # он вернет нам обратный вызов к сокету, данные полученные из
                # сокета сохраним в контексте.
                incoming_data = blocking_read_callback()

                if not len(incoming_data):
                    # мы получили дескриптор как имеющий данные, однако данных
                    # нет. Вероятно сокет был закрыт клиентом поэтому уберем
                    # его из пула.
                    raise StopIteration()

                connection_context.io_callable = session_coroutine.send(incoming_data)
            except StopIteration:
                session_coroutine.close()
                user_sessions_data.pop(descriptor)
                sockets_pool.remove(descriptor)
                print('Closed connection. Currently %d %s' % (len(sockets_pool),
                                                              sockets_pool))


if __name__ == '__main__':

    MODE_XINETD = 'xinetd'
    MODE_STANDALONE = 'standalone'

    parser = OptionParser()
    parser.add_option("-m", "--mode", choices=[MODE_XINETD, MODE_STANDALONE],
                      default=MODE_STANDALONE, dest="mode")
    (options, args) = parser.parse_args()

    if options.mode == MODE_XINETD:
        xinetd_io_loop()

    elif options.mode == MODE_STANDALONE:
        standalone_io_loop()
