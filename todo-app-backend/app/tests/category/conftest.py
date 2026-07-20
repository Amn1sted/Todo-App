import pytest

from app.services.category import CategoryService
from unittest.mock import create_autospec
from app.repositories.category import CategoryRepository
from app.models.category import CategoryORM
from app.main import app
from app.api.dependencies import get_category_service
from fastapi.testclient import TestClient
from typing import Generator


@pytest.fixture
def mock_category_service() -> CategoryService:
    """Фикстура для мока category_service.
    По факту возвращает гибрид CategoryService и MagicMock
    """
    return create_autospec(CategoryService, instance=True) # type: ignore[return-value]


@pytest.fixture
def test_category_repository(test_db) -> CategoryRepository:
    """Фикстура тестового category_repository"""
    db = test_db
    return CategoryRepository(db)


@pytest.fixture
def test_category_service(test_db) -> CategoryService:
    """Фикстура тестового category_service. Кэш обязательно мокается отдельно внутри тестов"""
    return CategoryService(db=test_db)


@pytest.fixture
def create_start_category(test_category_repository) -> CategoryORM:
    """Фикстура для создания стартовой категории"""
    category = test_category_repository.create(name='Стартовая категория')

    test_category_repository.db.flush()

    return category


@pytest.fixture
def test_client(mock_category_service) -> Generator[TestClient, None, None]:
    """Фикстура для обрезания сервиса для API тестов category"""
    app.dependency_overrides[get_category_service] = lambda: mock_category_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()