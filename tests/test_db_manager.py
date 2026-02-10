from src.db_manager import DBManager
from unittest.mock import Mock, patch


def test_basic_dbmanager():
    """Базовый тест инициализации DBManager"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = DBManager("mydb", "user", "pass")

        assert db.conn == mock_conn
        assert db.cursor == mock_cursor
        assert mock_conn.autocommit is True

        print("✓ test_basic_dbmanager: PASSED")


def test_create_tables_basic():
    """Базовый тест создания таблиц"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = DBManager("test", "test", "test")
        db.create_tables()

        # Проверяем, что было 2 вызова execute
        assert mock_cursor.execute.call_count == 2

        print("✓ test_create_tables_basic: PASSED")


def test_insert_employer_basic():
    """Базовый тест вставки работодателя"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (123,)

        db = DBManager("test", "test", "test")

        employer_data = {
            "employer_id": "123",
            "company": "Test Co",
            "description": "Desc",
            "url": "https://test.com"
        }

        result = db.insert_employer(employer_data)

        assert result == 123
        assert mock_cursor.execute.called

        print("✓ test_insert_employer_basic: PASSED")


def test_insert_vacancy_basic():
    """Базовый тест вставки вакансии"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (456,)

        db = DBManager("test", "test", "test")

        vacancy_data = {
            "vacancy_id": "456",
            "title": "Developer",
            "url": "https://test.com"
        }

        result = db.insert_vacancy(123, vacancy_data)

        assert result == 456
        assert mock_cursor.execute.called

        print("✓ test_insert_vacancy_basic: PASSED")


def test_get_all_vacancies():
    """Тест получения всех вакансий"""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Настраиваем возвращаемые данные
        mock_cursor.description = [
            ('title',), ('salary_from',), ('salary_to',),
            ('currency',), ('url',), ('employer_name',)
        ]
        mock_cursor.fetchall.return_value = [
            ('Python Dev', 100000, 150000, 'RUR', 'https://test.com', 'Test Co')
        ]

        db = DBManager("test", "test", "test")
        result = db.get_all_vacancies()

        assert len(result) == 1
        assert result[0]['title'] == 'Python Dev'
        assert result[0]['employer_name'] == 'Test Co'

        print("✓ test_get_all_vacancies: PASSED")

