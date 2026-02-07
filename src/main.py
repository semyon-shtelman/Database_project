import os
import time

from dotenv import load_dotenv

from employer import Employer
from src.db_manager import DBManager
from src.hh_api import HeadHunterAPI
from vacancy import Vacancy

# Словарь работодателей: название -> id в HH
EMPLOYERS = {
    "Яндекс": 1740,
    "Сбер": 3529,
    "VK": 15478,
    "Тинькофф": 78638,
    "Ozon": 2180,
    "Wildberries": 87021,
    "Газпром": 39305,
    "Альфа-Банк": 80,
    "Ростелеком": 2748,
    "МТС": 3776,
}


def user_menu(db: DBManager) -> None:
    """Интерактивное меню для пользователя"""

    while True:
        print("\nВыберите действие:")
        print("1 — Показать все вакансии")
        print("2 — Показать вакансии с зарплатой выше средней")
        print("3 — Поиск вакансий по ключевому слову")
        print("4 — Показать количество вакансий по компаниям")
        print("5 — Показать среднею зарплату по всем вакансиям")
        print("0 — Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            vacancies = db.get_all_vacancies()
            print("\nВсе вакансии:\n")
            for v in vacancies:
                print(
                    f"Компания: {v['employer_name']} | "
                    f"Вакансия: {v['title']} | "
                    f"Зарплата: {v['salary_from']} - {v['salary_to']} {v['currency']} | "
                    f"Ссылка: {v['url']}"
                )

        elif choice == "2":
            vacancies = db.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:\n")
            for v in vacancies:
                print(
                    f"Компания: {v['employer_name']} | "
                    f"Вакансия: {v['title']} | "
                    f"Зарплата: {v['salary_from']} - {v['salary_to']} {v['currency']} | "
                    f"Ссылка: {v['url']}"
                )

        elif choice == "3":
            keyword = input("Введите ключевое слово: ").strip()
            vacancies = db.get_vacancies_with_keyword(keyword)
            print(f"\nВакансии по ключевому слову «{keyword}»:\n")
            for v in vacancies:
                print(
                    f"Компания: {v['employer_name']} | "
                    f"Вакансия: {v['title']} | "
                    f"Зарплата: {v['salary_from']} - {v['salary_to']} {v['currency']} | "
                    f"Ссылка: {v['url']}"
                )
        elif choice == "4":
            company_stats = db.get_companies_and_vacancies_count()
            print("\nКоличество вакансий по компаниям:\n")
            for stat in company_stats:
                print(f"Компания: {stat['company']} | Вакансий: {stat['vacancies_count']}")

        elif choice == "5":
            avg_salary = db.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f}")

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный ввод, попробуйте ещё раз.")


def main() -> None:
    """Основная функция для заполнения базы данных"""
    load_dotenv()
    # Данные для подключения к PostgreSQL
    DB_CONFIG = {
        "dbname": f"{os.getenv("DATABASE_NAME")}",
        "user": f"{os.getenv("DATABASE_USER")}",
        "password": f"{os.getenv("DATABASE_PASSWORD")}",  # Замените на ваш пароль
        "host": f"{os.getenv("DATABASE_HOST")}",
        "port": f"{os.getenv("DATABASE_PORT")}",
    }

    try:
        # Создаем подключение к базе данных
        print("Подключаемся к базе данных...")
        db = DBManager(**DB_CONFIG)
        # db.reset_database()
        # Создаем таблицы
        print("Создаем таблицы...")

        # Создаем экземпляр API для работы с HeadHunter
        print("Инициализируем API HeadHunter...")
        hh_api = HeadHunterAPI()

        total_employers = 0
        total_vacancies = 0

        # Обрабатываем каждого работодателя
        for employer_name, employer_id in EMPLOYERS.items():
            print(f"\n{'=' * 60}")
            print(f"Обработка работодателя: {employer_name} (ID: {employer_id})")
            print("=" * 60)

            try:
                # Получаем информацию о работодателе
                print("Получаем информацию о работодателе...")
                employer_data = hh_api.get_employer_info(employer_id)

                # Преобразуем данные в объект Employer
                employer_obj = Employer.cast_to_object(employer_data)
                employer_dict = employer_obj.to_dict()

                # Добавляем работодателя в базу данных
                print(f"Добавляем работодателя {employer_name} в БД...")
                db.insert_employer(employer_dict)
                total_employers += 1

                # Получаем вакансии работодателя
                print("Получаем вакансии работодателя...")
                vacancies_data = hh_api.get_vacancies(employer_id)

                # Преобразуем данные в список объектов Vacancy
                vacancy_objects = Vacancy.cast_to_object_list(vacancies_data)

                # Добавляем вакансии в базу данных
                vacancies_added = 0
                for vacancy in vacancy_objects:
                    vacancy_dict = vacancy.to_dict()
                    # Добавляем вакансию в БД
                    db.insert_vacancy(employer_id, vacancy_dict)

                # Пауза между запросами к API, чтобы не превысить лимиты
                time.sleep(0.1)

            except Exception as e:
                print(f"Ошибка при обработке работодателя {employer_name}: {e}")
                continue

        # Запуск пользовательского меню
        user_menu(db)

        # Закрываем соединение с БД
        db.close()
        print("\nБаза данных успешно заполнена!")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
