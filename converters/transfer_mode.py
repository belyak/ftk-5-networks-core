import converters.definitions


class TransferMode():
    """
    Класс обеспечивающий выставление режима передачи и фактическое его применение
    только после следующего запроса режима передачи.
    """
    def __init__(self):
        self.__current_mode = converters.definitions.MODE_PLAIN
        self.__next_mode = None

    @property
    def mode(self):
        """
        получение режима передачи
        """
        transfer_mode = self.__current_mode
        if self.__next_mode:
            self.__current_mode = self.__next_mode
            self.__next_mode = None
        return transfer_mode

    @mode.setter
    def mode(self, transfer_mode):
        """
        Выставление режима для следующей передачи
        """
        self.__next_mode = transfer_mode