LINES_DELIMITER = '\r\n'
B_LINES_DELIMITER = LINES_DELIMITER.encode()

VERSION = 0.01
HELLO_MSG = 'Text frequency analysis server v.%s ready.' % VERSION

CODE_OK = 200
CODE_BAD_DATA = 400
CODE_NOT_FOUND = 404

MSG_PL_LINE_HAS_BEEN_COLLECTED = 'line has been collected (%d at the moment).'
MSG_PT_TEXT_HAS_BEEN_COLLECTED = '%d lines has been collected (%d total)'

MSG_ENC_ENCODING_HAS_BEEN_SET = 'Encoding has been set to "%s"'
ERR_ENCODING_NOT_FOUND = 'encoding "%s" not found!'

MSG_CALCULATED_LINES_WORDS = 'Calculated (%d lines, %d words)'

MSG_STATISTICS_HAS_BEEN_LOADED = 'Statistics "%s" has been loaded.'
ERR_STATISTICS_NOT_FOUND = 'Statistics "%s" not found!'

MSG_STATISTICS_HAS_BEEN_SAVED = 'Statistics "%s" has been saved'

MSG_STATISTICS_HAS_BEEN_MERGED = 'Statistics "%s" has been merge into current'
MSG_STATISTICS_TO_MERGE_NOT_FOUND = 'Statistics "%s" has not been loaded!!!'

ERR_COMMAND_NOT_RECOGNIZED = 'Command cannot be recognized!'
