import requests


class HeadHunterAPI:
    """
    Класс для работы с API hh.ru
    Позволяет получать информацию о работодателях и их вакансиях.
    """

    __BASE_URL = "https://api.hh.ru"

    def __init__(self) -> None:
        """Инициализация объекта API.
        Создает заголовки для запросов
        """
        self.__headers = {"User-Agent": "HH-API-Student-Project"}

    def __connect(self, url: str, params: dict) -> dict:
        """
        Приватный метод подключения к API hh.ru
        """
        response = requests.get(url, headers=self.__headers, params=params)
        if response.status_code != 200:
            raise ConnectionError("Ошибка подключения к hh.ru")
        return response.json()

    def get_employer_info(self, employer_id: int) -> dict:
        """
        Получение информации о работодателе по его ID.
        :param employer_id: Уникальный идентификатор работодателя на hh.ru.
        :return:Словарь с данными о работодателе, как их возвращает hh.ru.
        """
        emp_api_url = f"{self.__BASE_URL}/employers/{employer_id}"
        return self.__connect(emp_api_url, {})

    def get_vacancies(self, employer_id: int) -> list:
        """
        Получение списка вакансий конкретного работодателя.
        :param employer_id: Уникальный идентификатор работодателя на hh.ru.
        :return: Список вакансий в формате словаря, каждая вакансия как dict.
        """

        vacancies = []

        vacancies_url = f"{self.__BASE_URL}/vacancies"

        params = {"employer_id": employer_id, "per_page": 100}  # берем первые 100 вакансий

        vac_response = self.__connect(vacancies_url, params)["items"]
        vacancies.extend(vac_response)
        return vacancies
