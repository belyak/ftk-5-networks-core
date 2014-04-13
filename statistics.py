import os
import json
import hashlib

import settings


class StatisticsNotFound(KeyError):
    """
    Исключение, порождаемое при попытке получить несуществующий объект типа Statistics
    """
    pass


class Statistics():
    """
    Класс для работы с частотной статистикой текстов.
    """

    def __init__(self, name, data=None):
        """
        Создание объекта статистики
        :param name: имя статистики
        :type name: str
        :param data: данные
        :type data: dict or None
        """
        self._name = name
        self._data = data if data is not None else {}

    @classmethod
    def load(cls, name):
        """
        Загрузка статистики.
        В случае невозможности загрузить статистику с именем name возбуждает исключение StatisticsNotFound
        :param name: имя статистики
        :type name: str
        :raises: StatisticsNotFound
        :rtype: Statistics
        """
        raise NotImplementedError()

    def save(self, name=None):
        """
        Сохранение статистики под указанным именем, либо под текущим, если имя не указано.
        В случае сохранения под новым именем имя статистики изменяется, т.е. в дальнейшем класс работает с новым набором
        данных старый набор данных остается без изменений.

        :param name: Имя, под которым будет сохранена статистика, текущее если не указано
        :type name: str or None
        """
        raise NotImplementedError()

    def __setitem__(self, key, value):
        self._data[key] = value

    def get(self):
        return self._data


def statistics_name_to_filename(name):
    """
    :type name: str
    :rtype; str
    """
    filename = '%s.json' % hashlib.md5(name.encode()).hexdigest()
    return os.path.join(settings.DATA_DIR, filename)


class FileStatistics(Statistics):
    @classmethod
    def load(cls, name):
        filename = statistics_name_to_filename(name)
        try:
            with open(filename, 'r') as f:
                contents = f.read()
        except FileNotFoundError:
            raise StatisticsNotFound(name)

        data = json.loads(contents)

        return Statistics(name, data)

    def save(self, name=None):
        if name is not None:
            self._name = name
        filename = statistics_name_to_filename(self._name)
        contents = json.dumps(self._data, ensure_ascii=False)
        with open(filename, 'w') as f:
            f.write(contents)