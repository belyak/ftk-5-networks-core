class AbstractConverter():
    """
    Базовый класс для всех конвертеров
    """
    ENCODED_CHUNK_LEN = None  # длина кодированного сообщения
    """:type: int"""

    def encode(self, normal_message):
        """
        :param bytes normal_message: сообщение которое требуется закодировать
        :rtype bytes:
        """
        raise NotImplementedError()

    def decode(self, encoded_message):
        """
        :param bytes seven_bit_message: закодированное сообщение, которое требуется декодировать.
        :rtype: bytes
        """
        raise NotImplementedError()