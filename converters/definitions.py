from converters.plain_converter import PlainConverter
from converters.seven_bit_converter import SevenBitConverter
from converters.base64_converter import Base64Converter

MODE_PLAIN = 'plain'
MODE_7BIT = '7bit'
MODE_BASE64 = 'base64'

CONVERTER_BY_MODE = {
    MODE_PLAIN: PlainConverter(),
    MODE_7BIT: SevenBitConverter(),
    MODE_BASE64: Base64Converter(),
}
