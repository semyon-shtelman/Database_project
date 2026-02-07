class Employer:
    """
    Класс для представления работодателя.
    """

    def __init__(self, employer_id: int, company: str, description: str, url: str):
        """
        Инициализация объекта Employer.

        :param employer_id: Уникальный идентификатор работодателя.
        :param company: Название компании.
        :param description: Краткое описание компании.
        :param url: Ссылка на страницу работодателя на hh.ru.
        """
        self.employer_id = employer_id
        self.company = company
        self.description = description
        self.url = url

    @classmethod
    def cast_to_object(cls, data: dict) -> "Employer":
        """
        Создание объекта Employer из словаря с данными, полученного от API.

        :param data: Словарь с данными о работодателе
        :return: Объект класса Employer.
        """
        description = f"{data.get("description", "Нет описания")[:200]}..."
        emp_url = data.get("alternate_url") or ""

        return cls(
            employer_id=data["id"],
            company=data["name"],
            description=description,
            url=emp_url,
        )

    def to_dict(self) -> dict:
        """
        Преобразует объект Employer в словарь для вставки в базу данных
        :return: Словарь с атрибутами работодателя
        """
        return {
            "employer_id": self.employer_id,
            "company": self.company,
            "description": self.description,
            "url": self.url,
        }
