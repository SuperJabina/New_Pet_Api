from datetime import date, timedelta

from faker import Faker


class Fake:
    """
    Класс-обертка над Faker, предоставляющий удобные методы генерации фейковых данных
    для банковских операций.
    """
    def __init__(self, faker: Faker):
        """
        Инициализирует объект Fake с экземпляром Faker.

        :param faker: Экземпляр Faker для генерации случайных данных.
        """
        self.faker = faker

    def date(self, start: timedelta = timedelta(days=-30), end: timedelta = timedelta()) -> date:
        """
        Генерирует случайную дату в заданном диапазоне.

        :param start: Начальный диапазон (по умолчанию -30 дней от текущей даты).
        :param end: Конечный диапазон (по умолчанию сегодняшняя дата).
        :return: Случайная дата в заданном диапазоне.
        """
        return self.faker.date_between(start_date=start, end_date=end)

    def money(self, start: float = -100, end: float = 100) -> float:
        """
        Генерирует случайную сумму денег.

        :param start: Минимальное значение (по умолчанию -100).
        :param end: Максимальное значение (по умолчанию 100).
        :return: Случайное число с плавающей запятой в заданном диапазоне.
        """
        return self.faker.pyfloat(min_value=start, max_value=end)

    def category(self) -> str:
        """
        Генерирует случайную категорию расходов.

        :return: Одна из предопределенных категорий ('food', 'taxi', 'fuel' и т.д.).
        """
        return self.faker.random_element(['food', 'taxi', 'fuel', 'beauty', 'restaurants'])

    def sentence(self) -> str:
        """
        Генерирует случайное описание операции.

        :return: Строка с описанием.
        """
        return self.faker.sentence()


# Создаем глобальный экземпляр `fake`, который будем использовать в других модулях.
fake = Fake(faker=Faker())