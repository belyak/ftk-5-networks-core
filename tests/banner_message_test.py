from unittest import TestCase
from unittest.mock import patch
import banner_message


class BannerMessageTest(TestCase):
    """
    Проверяет, что класс составляет корректное сообщение в формате описаном в спецификации протокола
    для независимости теста от внешнего кода используется подмена объектов, к которым обращается код
    класса.
    """
    @patch(target='constants.HELLO_MSG', new='DUMMY HELLO')
    @patch(target='commands.COMMANDS', new=[('A',), ('B',), ('CD',)])
    @patch(target='converters.definitions.CONVERTER_BY_MODE', new={'M1': None, 'M2': None})
    def test_get(self):
        bm = banner_message.BannerMessage.get()
        expected_result = "DUMMY HELLO SC:A,B,CD. SM:M1,M2."
        self.assertEquals(bm, expected_result)