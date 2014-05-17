from unittest import TestCase
from constants import LINES_DELIMITER

from utils import create_message


class TestCreateMessage(TestCase):
    def test_create_message_single_line(self):
        code = 200
        line = 'Status OK.'
        expected_result = '200 Status OK.'

        result = create_message(code, line, as_bytes=False)
        self.assertEqual(result, expected_result)

    def test_create_message_multiple_lines(self):
        code = 200
        text = LINES_DELIMITER.join([
            'line 1',
            'line 2',
            'line 3'
        ])

        expected_result = LINES_DELIMITER.join([
            '200-line 1',
            'line 2',
            '200 line 3'
        ])

        result = create_message(code, text, as_bytes=False)
        self.assertEqual(expected_result, result)
