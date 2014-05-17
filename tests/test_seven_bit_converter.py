from unittest import TestCase
from seven_bit_converter import SevenBitConverter


class SevenBitConverterTest(TestCase):

    def setUp(self):
        super().setUp()
        self.converter = SevenBitConverter()


    def test_encode_divisible_case(self):
        """
        Проверка перекодирования сообщения, кратный случай:
        текстовое сообщение 7 байт по 8 бит --> 8 байт по 7 бит
        """
        normal_bytes = bytes([200, 200, 200, 200, 200, 200, 200])
        expected_7bit = bytes([100, 50, 25, 12, 70, 35, 17, 72])

        result_7bit = self.converter.encode(normal_bytes)

        self.assertEquals(expected_7bit, result_7bit)

    # def test_encode_non_divisible_case(self):
    #     self.fail()
    #
    # def test_decode(self):
    #     self.fail()