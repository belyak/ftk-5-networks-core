from unittest import TestCase
from persistent_statistics import FilePersistentStatistics

from statistics import Statistics
from tests.tst_data import TEST_TEXT, TEST_DATA


class TestStatistics(TestCase):
    def setUp(self):
        self.statistics = Statistics(storage=FilePersistentStatistics('test'))

    def test_lines_count(self):

        lines_count = 10

        for _ in range(lines_count):
            self.statistics.put_line('some line')

        self.assertEqual(self.statistics.lines_count, lines_count)

    def test_words_count(self):

        words_count = 5

        for line in ('wordOne wordTwo', 'wordThree wordFour', 'wordFive'):
            self.statistics.put_line(line)

        self.statistics.calc()
        self.assertEquals(self.statistics.words_count, words_count)

    def test_calc(self):
        for line in TEST_TEXT.split('\n'):
            self.statistics.put_line(line)

        self.statistics.calc()

        calculated_stats = self.statistics.get()

        self.assertEqual(calculated_stats, TEST_DATA)