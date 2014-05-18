from unittest import TestCase

from converters.seven_bit_converter import SevenBitConverter


class SevenBitConverterTest(TestCase):

    def setUp(self):
        super().setUp()
        self.converter = SevenBitConverter()
        self.normal_bytes = bytes([200, 200, 200, 200, 200, 200, 200])
        self.encoded_7_bits = bytes([100, 50, 25, 12, 70, 35, 17, 72])

    def test_encode_divisible_case(self):
        """
        Проверка перекодирования сообщения, кратный случай:
        текстовое сообщение 7 байт по 8 бит --> 8 байт по 7 бит
        """

        result_7bit = self.converter.encode(self.normal_bytes)

        self.assertEquals(self.encoded_7_bits, result_7bit)

    def test_encode_non_divisible_case(self):
        """
        проверка кодирования сообщения не кратного 7 байтам
        """
        original_message = b'YES\r\n'
        expected_decoded = bytes([44, 81, 42, 50, 1, 0, 26, 10])
        decoded_result = self.converter.encode(original_message)
        self.assertEquals(expected_decoded, decoded_result)

    def test_decode(self):
        """
        проверка декодирования 7бит в 8бит, кратный случай.
        сообщение 8 байт с 7 значащими битами в 7 "нормальных" байт
        """
        result_8bit = self.converter.decode(self.encoded_7_bits)

        self.assertEquals(self.normal_bytes, result_8bit)