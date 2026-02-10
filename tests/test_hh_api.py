from src.hh_api import HeadHunterAPI
from unittest.mock import Mock, patch


@patch('requests.get')
def test_get_employer_info_mocked(mock_get):
    """Тест get_employer_info с mock"""
    # Настраиваем mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "123", "name": "Test Co"}
    mock_get.return_value = mock_response

    api = HeadHunterAPI()
    result = api.get_employer_info(123)

    assert result["id"] == "123"
    assert result["name"] == "Test Co"

    print("✓ test_get_employer_info_mocked: PASSED")


@patch('requests.get')
def test_get_vacancies_mocked(mock_get):
    """Тест get_vacancies с mock"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"id": "1", "name": "Job 1"},
            {"id": "2", "name": "Job 2"}
        ]
    }
    mock_get.return_value = mock_response

    api = HeadHunterAPI()
    result = api.get_vacancies(123)

    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"
