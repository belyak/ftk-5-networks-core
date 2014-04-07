from unittest import TestCase

from utils import create_message


class TestCreateMessage(TestCase):
    def test_create_message_single_line(self):
        code = 200
        line = 'Status OK.'
        expected_result = '200 Status OK.'

        result = create_message(code, line)
        self.assertEqual(result, expected_result)

    def test_create_message_multiple_lines(self):
        code = 200
        text = '\n'.join([
            'line 1',
            'line 2',
            'line 3'
        ])

        expected_result = '\n'.join([
            '200-line 1',
            'line 2',
            '200 line 3'
        ])

        result = create_message(code, text)
        self.assertEqual(expected_result, result)