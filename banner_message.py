import commands
import constants
import converters.definitions


class BannerMessage():
    __banner_message = None

    @classmethod
    def get(cls):
        """
        Возвращает banner message при первом вызове составляя его из
        приветственного сообщения и списка комманд.
        """
        if not cls.__banner_message:
            commands_keywords = sorted([c[0] for c in commands.COMMANDS])
            supported_modes = sorted(
                converters.definitions.CONVERTER_BY_MODE.keys()
            )
            cls.__banner_message = '%s SC:%s. SM:%s.' % (constants.HELLO_MSG,
                                                         ','.join(commands_keywords),
                                                         ','.join(supported_modes))

        return cls.__banner_message