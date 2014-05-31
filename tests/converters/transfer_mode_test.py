from unittest import TestCase
from converters.transfer_mode import TransferMode
from converters.definitions import MODE_PLAIN, MODE_7BIT, MODE_BASE64


class TransferModeTest(TestCase):
    """
    Класс тестирующий отложенный возврат нового режима передачи классом TransferMode
    """
    def test_mode(self):
        transfer_mode = TransferMode()

        # проверим что по умолчанию класс вернет режим plain

        initial_mode = transfer_mode.mode
        self.assertEquals(initial_mode, MODE_PLAIN)

        transfer_mode.mode = MODE_7BIT
        # проверим что при следующем чтении будет возвращен предыдущий режим:
        mode = transfer_mode.mode
        self.assertEquals(mode, MODE_PLAIN)
        # проверим что при втором чтении произойдет переключение режима и вернется новый режим:
        mode = transfer_mode.mode
        self.assertEquals(mode, MODE_7BIT)

        # аналогично проверим отложенное переключение в режим base64
        transfer_mode.mode = MODE_BASE64
        mode = transfer_mode.mode
        self.assertEquals(mode, MODE_7BIT)
        mode = transfer_mode.mode
        self.assertEquals(mode, MODE_BASE64)