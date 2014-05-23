from commands import COMMANDS
from constants import HELLO_MSG
from converters.definitions import CONVERTER_BY_MODE


class BannerMessage():
    __banner_message = None

    @classmethod
    def get(cls):
        """
        Возвращает banner message при первом вызове составляя его из приветственного сообщения и списка комманд.
        """
        if not cls.__banner_message:
            commands_keywords = sorted([c[0] for c in COMMANDS])
            supported_modes = CONVERTER_BY_MODE.keys()
            cls.__banner_message = '%s SC:%s. SM:%s.' % (HELLO_MSG, ','.join(commands_keywords),
                                                         ','.join(supported_modes))

        return cls.__banner_message