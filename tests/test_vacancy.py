from src.vacancy import Vacancy

def test_basic_vacancy_creation():
    """Базовый тест создания вакансии"""
    vacancy = Vacancy(
        vacancy_id=1,
        title="Test",
        url="https://test.com",
        salary_from=100000,
        salary_to=150000,
        currency="RUR",
        description="Test description"
    )

    assert vacancy.title == "Test"
    assert vacancy.salary_from == 100000


def test_vacancy_no_salary():
    """Тест вакансии без зарплаты"""
    vacancy = Vacancy(
        vacancy_id=2,
        title="No Salary",
        url="https://test.com",
        salary_from=None,
        salary_to=None,
        currency="USD",
        description="No salary"
    )

    assert vacancy.salary_from == 0
    assert vacancy.salary_to == 0
    assert vacancy.currency == ""


def test_vacancy_comparison_simple():
    """Простой тест сравнения вакансий"""
    v1 = Vacancy(1, "Low", "", 50000, 60000, "RUR", "")
    v2 = Vacancy(2, "High", "", 100000, 120000, "RUR", "")

    assert v1 < v2
    assert v2 > v1


def test_vacancy_from_api_data():
    """Тест создания вакансии из API данных"""
    api_data = [
        {
            "id": 123,
            "name": "API Job",
            "alternate_url": "https://api.example.com",
            "salary": {"from": 80000, "to": 120000, "currency": "RUR"},
            "snippet": {"requirement": "API skills"}
        }
    ]

    vacancies = Vacancy.cast_to_object_list(api_data)

    assert len(vacancies) == 1
    assert vacancies[0].title == "API Job"
    assert vacancies[0].salary_from == 80000