from unittest import TestCase

import uuid
from statistics import FileStatistics, StatisticsNotFound

TEST_DATA = {
    'GREAT': 1,
    'HUMPTY': 3,
    'SAT': 1,
    'THE': 3,
    'MAN': 1,
    'HAD': 1,
    'FALL': 1,
    'WALL': 1,
    'ON': 1,
    'HORSES': 1,
    'ALL': 2,
    'TOGETHER': 1,
    'PUT': 1,
    'DUMPTY': 2,
    'KING': 2,
    'A': 1,
    'AND': 1,
    'AGAIN': 1
}


class TestFileStatistics(TestCase):
    def test_save_and_load_consistency(self):

        name = 'test_statistics'

        statistics = FileStatistics(name=name, data=TEST_DATA)
        statistics.save()

        loaded_statistics = FileStatistics.load(name)

        loaded_data = loaded_statistics.get()

        self.assertEqual(loaded_data, TEST_DATA)

    def test_not_found_statistics(self):

        # сгенерируем уникальный идентификатор и попробуем полуить статистику с таким именем
        # очевидно, что есть некоторая вероятность, что такой файл будет существовать, но мы ей пренебрежем.
        unique_name = uuid.uuid4().hex

        self.assertRaises(StatisticsNotFound, FileStatistics.load, name=unique_name)