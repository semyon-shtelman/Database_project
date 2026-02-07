from typing import Dict, List, Optional


class Vacancy:
    """
    Класс для представления вакансии.

    Экземпляр класса содержит основную информацию о вакансии:
    название, ссылку, диапазон зарплат, валюту и описание.
    Поддерживает сравнение вакансий между собой по уровню зарплаты.
    """

    __slots__ = ("vacancy_id", "title", "url", "salary_from", "salary_to", "currency", "description")

    def __init__(
        self,
        vacancy_id: int,
        title: str,
        url: str,
        salary_from: Optional[int],
        salary_to: Optional[int],
        currency: Optional[str],
        description: str,
    ):
        """
        Инициализирует объект вакансии.

        В процессе инициализации:
        - валидируются значения зарплаты;
        - при отсутствии данных о зарплате валюта не устанавливается.

        :param title: Название вакансии
        :param url: ссылка на вакансию
        :param salary_from: нижняя граница зарплаты
        :param salary_to: верхняя граница зарплаты
        :param currency: валюта заработной платы
        :param description: краткое описание или требования вакансии
        """
        self.vacancy_id = vacancy_id
        self.title = title
        self.url = url
        self.salary_from = self.__validate_salary(salary_from)
        self.salary_to = self.__validate_salary(salary_to)
        self.currency = currency if self.salary_from or self.salary_to else ""
        self.description = description

    @staticmethod
    def __validate_salary(value: Optional[int]) -> int:
        """
        Валидирует значение зарплаты.

        Если значение не является целым числом,
        возвращается 0 (зарплата не указана).

        :param value: Значение зарплаты
        :return: корректное значение зарплаты
        """
        return value if isinstance(value, int) else 0

    def __lt__(self, other: "Vacancy") -> bool:
        """
        Сравнивает вакансии по минимальной зарплате (меньше).

        :param other: Другая вакансия для сравнения
        :return: True, если зарплата текущей вакансии меньше
        """
        return self.salary_from < other.salary_from

    def __gt__(self, other: "Vacancy") -> bool:
        """
        Сравнивает вакансии по минимальной зарплате (больше).

        :param other: Другая вакансия для сравнения
        :return: True, если зарплата текущей вакансии больше
        """
        return self.salary_from > other.salary_from

    @classmethod
    def cast_to_object_list(cls, data: List[Dict]) -> List["Vacancy"]:
        """
        Преобразует список словарей с данными вакансий
        в список объектов класса Vacancy.

        Используется для преобразования данных,
        полученных из API hh.ru, в объекты вакансий.

        :param data: Данные полученных из API hh.ru
        :return: Список объектов класса Vacancy
        """
        vacancies = []
        for item in data:
            salary = item.get("salary") or {}
            vacancies.append(
                cls(
                    vacancy_id=item["id"],
                    title=item["name"],
                    url=item["alternate_url"],
                    salary_from=salary.get("from"),
                    salary_to=salary.get("to"),
                    currency=salary.get("currency"),
                    description=item.get("snippet", {}).get("requirement", ""),
                )
            )
        return vacancies

    def to_dict(self) -> dict:
        """
        Преобразует объект вакансии в словарь.

        Используется для сохранения вакансии.
        :return: Словарь с атрибутами вакансии
        """
        return {
            "vacancy_id": self.vacancy_id,
            "title": self.title,
            "url": self.url,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to,
            "currency": self.currency,
            "description": self.description,
        }
