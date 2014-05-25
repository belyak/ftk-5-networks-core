import base64

from converters.abstract_converter import AbstractConverter


class Base64Converter(AbstractConverter):
    ENCODED_CHUNK_LEN = 4

    def encode(self, normal_message):
        return base64.standard_b64encode(normal_message)

    def decode(self, encoded_message):
        return base64.standard_b64decode(encoded_message)