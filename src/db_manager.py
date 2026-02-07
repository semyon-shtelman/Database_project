from typing import Any, Dict, List

import psycopg2


class DBManager:
    """Класс для управления базой данных PostgreSQL"""

    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: str = "5432"):
        """
        Инициализация подключения к базе данных

        Args:
            dbname: Имя базы данных
            user: Имя пользователя
            password: Пароль
            host: Хост (по умолчанию localhost)
            port: Порт (по умолчанию 5432)
        """
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def reset_database(self) -> None:
        """Удаляет таблицы и создаёт их заново"""
        print("Сбрасываем базу данных...")
        self.cursor.execute("DROP TABLE IF EXISTS vacancies CASCADE;")
        self.cursor.execute("DROP TABLE IF EXISTS employers CASCADE;")
        print("Таблицы удалены.")
        self.create_tables()

    def create_tables(self) -> None:
        """Создание таблиц employers и vacancies"""
        # Таблица работодателей
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id SERIAL PRIMARY KEY,
                company VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                description TEXT
            )
        """)

        # Таблица вакансий
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id BIGINT PRIMARY KEY,
            employer_id BIGINT REFERENCES employers(employer_id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            currency VARCHAR(10),
            url VARCHAR(255) NOT NULL,
            description TEXT
            )
            """)

    def insert_employer(self, employer_data: Dict[str, Any]) -> int:
        """
        Вставка данных о работодателе

        Args:
            employer_data: Словарь с данными работодателя

        Returns:
            ID вставленной записи
        """
        query = """
                INSERT INTO employers (employer_id, company, description, url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (employer_id) DO UPDATE SET
                    company = EXCLUDED.company,
                    description = EXCLUDED.description,
                    url = EXCLUDED.url
                RETURNING employer_id
            """
        self.cursor.execute(
            query,
            (
                int(employer_data["employer_id"]),
                employer_data["company"],
                employer_data.get("description", ""),
                employer_data.get("url", ""),
            ),
        )
        result = self.cursor.fetchone()
        if not result:
            raise ValueError("Не удалось вставить работодателя")
        return int(result[0])

    def insert_vacancy(self, employer_id: int, vacancy_data: Dict[str, Any]) -> int:
        """
        Вставка данных о вакансиях
        :param employer_id: id - работодателя
        :param vacancy_data: данные с вакансиями
        :return:
        """

        query = """
               INSERT INTO vacancies
               (vacancy_id, employer_id, title, salary_from, salary_to, currency, url, description)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (vacancy_id) DO UPDATE SET
                   employer_id = EXCLUDED.employer_id,
                   title = EXCLUDED.title,
                   salary_from = EXCLUDED.salary_from,
                   salary_to = EXCLUDED.salary_to,
                   currency = EXCLUDED.currency,
                   url = EXCLUDED.url,
                   description = EXCLUDED.description
               RETURNING vacancy_id
               """

        self.cursor.execute(
            query,
            (
                int(vacancy_data["vacancy_id"]),
                int(employer_id),
                vacancy_data["title"],
                vacancy_data.get("salary_from"),
                vacancy_data.get("salary_to"),
                vacancy_data.get("currency"),
                vacancy_data["url"],
                vacancy_data.get("description", ""),
            ),
        )
        result = self.cursor.fetchone()
        if not result:
            raise ValueError("Не удалось вставить вакансию")
        return int(result[0])

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получение количества вакансий по компаниям"""
        query = """
            SELECT e.company, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.company
            ORDER BY vacancies_count DESC
        """
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получение всех вакансий"""
        query = """
            SELECT
            v.title,
            v.salary_from,
            v.salary_to,
            v.currency,
            v.url,
            e.company AS employer_name
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        """
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_avg_salary(self) -> float:
        """Получение средней зарплаты по всем вакансиям"""
        query = """
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return float(result[0]) if result[0] else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получение вакансий с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        query = """
            SELECT v.*, e.company as employer_name
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 > %s
            ORDER BY (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2 DESC
        """
        self.cursor.execute(query, (avg_salary,))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Поиск вакансий по ключевому слову в названии"""
        query = """
            SELECT v.*, e.company as employer_name
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.title) LIKE %s OR LOWER(v.description) LIKE %s
        """
        search_pattern = f"%{keyword.lower()}%"
        self.cursor.execute(query, (search_pattern, search_pattern))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]


    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        self.cursor.close()
        self.conn.close()
