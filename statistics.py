from collections import Counter
from persistent_statistics import PersistentStatistics, StatisticsNotFound

LETTERS = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'\
          'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'\
          'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
          'abcdefghijklmnopqrstuvwxyz\''


class Statistics():
    """
    Класс, реализующий статистический анализ текстов
    """
    def __init__(self, storage):
        """
        :param storage: объект, обеспечивающий персистентность статистики
        :type storage: PersistentStatistics
        """
        self.__lines = []
        self.__statistics = Counter()
        self.__storage = storage
        self.__words_count = 0

    def load(self, name):
        try:
            self.__storage = self.__storage.load(name)
            self.__statistics = Counter(self.__storage.data)
            return True
        except StatisticsNotFound:
            return False

    def save(self, name):
        self.__storage.data = dict(self.__statistics)
        return self.__storage.save(name)

    def merge(self, name):
        """
        дополняет содержимое текущей статистики статистикой с именем name
        """
        try:
            another_storage = self.__storage.load(name)
        except StatisticsNotFound:
            return False

        another_statistics = another_storage.data
        for word, count, in another_statistics.items():
            self.__statistics[word] += count
            self.__words_count += 1

        return True

    @property
    def lines_count(self):
        return len(self.__lines)

    @property
    def words_count(self):
        return self.__words_count

    def clear_buffer(self):
        """
        Очистка буфера строк
        """
        self.__lines.clear()
        self.__statistics.clear()
        self.__words_count = 0

    def put_line(self, line):
        """
        Добавление одной строки в буфер
        """
        self.__lines.append(line)

    def calc(self):
        """
        Расчет статистики для текста в буфере
        """
        words_processed = 0
        for line in self.__lines:
            letter_or_space = lambda c: c if c in LETTERS else ' '
            line = ''.join((letter_or_space(c) for c in line))
            words = (w.upper() for w in line.split(' ') if len(w))

            for word in words:
                self.__statistics[word] += 1
                words_processed += 1

        self.__words_count += words_processed

    def get(self):
        """
        Получение словаря статистики.
        """
        return dict(self.__statistics)