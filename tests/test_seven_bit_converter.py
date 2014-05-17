from unittest import TestCase
from seven_bit_converter import SevenBitConverter


class SevenBitConverterTest(TestCase):

    def setUp(self):
        super().setUp()
        self.converter = SevenBitConverter()
        self.normal_bytes = bytes([200, 200, 200, 200, 200, 200, 200])
        self.decoded_7_bits = bytes([100, 50, 25, 12, 70, 35, 17, 72])

    def test_encode_divisible_case(self):
        """
        Проверка перекодирования сообщения, кратный случай:
        текстовое сообщение 7 байт по 8 бит --> 8 байт по 7 бит
        """

        result_7bit = self.converter.encode(self.normal_bytes)

        self.assertEquals(self.decoded_7_bits, result_7bit)

    def test_decode(self):
        """
        проверка декодирования 7бит в 8бит, кратный случай.
        сообщение 8 байт с 7 значащими битами в 7 "нормальных" байт
        """
        result_8bit = self.converter.decode(self.decoded_7_bits)

        self.assertEquals(self.normal_bytes, result_8bit)