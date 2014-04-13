from collections import Counter

LETTERS = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'\
          'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'\
          'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
          'abcdefghijklmnopqrstuvwxyz\''


class Statistics():
    """
    Класс, реализующий статистический анализ текстов
    """
    def __init__(self):
        self.__lines = []
        self.__statistics = Counter()

    @property
    def lines_count(self):
        return len(self.__lines)

    def clear_buffer(self):
        """
        Очистка буфера строк
        """
        self.__lines.clear()
        self.__statistics.clear()

    def put_line(self, line):
        """
        Добавление одной строки в буфер
        """
        self.__lines.append(line)

    def calc(self):
        """
        Расчет статистики для текста в буфере
        """
        for line in self.__lines:
            letter_or_space = lambda c: c if c in LETTERS else ' '
            line = ''.join((letter_or_space(c) for c in line))
            words = (w.upper() for w in line.split(' ') if len(w))

            for word in words:
                self.__statistics[word] += 1

    def get(self):
        """
        Получение словаря статистики.
        """
        return dict(self.__statistics)