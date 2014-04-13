from unittest import TestCase

import uuid
from persistent_statistics import FilePersistentStatistics, StatisticsNotFound

from tests.tst_data import TEST_DATA


class TestFilePersistentStatistics(TestCase):
    def test_save_and_load_consistency(self):

        name = 'test_statistics'

        statistics = FilePersistentStatistics(name=name, data=TEST_DATA)
        statistics.save()

        loaded_statistics = FilePersistentStatistics.load(name)

        loaded_data = loaded_statistics.get()

        self.assertEqual(loaded_data, TEST_DATA)

    def test_not_found_statistics(self):

        # сгенерируем уникальный идентификатор и попробуем полуить статистику с таким именем
        # очевидно, что есть некоторая вероятность, что такой файл будет существовать, но мы ей пренебрежем.
        unique_name = uuid.uuid4().hex

        self.assertRaises(StatisticsNotFound, FilePersistentStatistics.load, name=unique_name)