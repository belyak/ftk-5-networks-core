from converters.abstract_converter import AbstractConverter


class PlainConverter(AbstractConverter):
    """
    Конвертер не изменяющий сообщения.
    """
    ENCODED_CHUNK_BYTES = 1

    def encode(self, normal_message):
        return normal_message

    def decode(self, encoded_message):
        return encoded_message