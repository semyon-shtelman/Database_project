from src.employer import Employer

def test_basic_employer():
    """Базовый тест создания работодателя"""
    emp = Employer(
        employer_id=1,
        company="Yandex",
        description="Russian IT company",
        url="https://hh.ru/employer/1"
    )

    assert emp.employer_id == 1
    assert emp.company == "Yandex"
    assert emp.url == "https://hh.ru/employer/1"


def test_from_api_data():
    """Тест создания из API данных"""
    api_data = {
        "id": "123",
        "name": "Yandex",
        "description": "Russian IT company",
        "alternate_url": "https://hh.ru/employer/123"
    }

    emp = Employer.cast_to_object(api_data)

    assert emp.employer_id == "123"
    assert emp.company == "Yandex"
    assert emp.description.startswith("Russian IT company")
    assert emp.url == "https://hh.ru/employer/123"


def test_to_dict_method():
    """Тест преобразования в словарь"""
    emp = Employer(2, "Apple", "iPhone maker", "https://hh.ru/employer/2")
    emp_dict = emp.to_dict()

    assert emp_dict["employer_id"] == 2
    assert emp_dict["company"] == "Apple"
    assert emp_dict["description"] == "iPhone maker"
    assert emp_dict["url"] == "https://hh.ru/employer/2"


def test_long_description():
    """Тест обрезки длинного описания"""
    long_desc = "A" * 250  # 250 символов
    api_data = {
        "id": "3",
        "name": "Test",
        "description": long_desc,
        "alternate_url": ""
    }

    emp = Employer.cast_to_object(api_data)

    # Должно обрезаться до 200 символов + "..."
    assert len(emp.description) == 203  # 200 + "..."
    assert emp.description.endswith("...")


def test_no_description_in_api():
    """Тест отсутствия описания в API"""
    api_data = {
        "id": "4",
        "name": "NoDesc Inc",
        "alternate_url": "https://test.com"
    }

    emp = Employer.cast_to_object(api_data)

    assert emp.description == "Нет описания..."

