import pytest

from app.services.task import TaskService
from app.repositories.task import TaskRepository
from app.models.task import TaskORM
from app.main import app
from app.api.dependencies import get_task_service
from fastapi.testclient import TestClient
from unittest.mock import create_autospec
from typing import Generator


@pytest.fixture
def mock_task_service() -> TaskService:
    """Фикстура для мока task_service.
    По факту возвращает гибрид TaskService и MagicMock
    """
    return create_autospec(TaskService, instance=True) # type: ignore[return-value]


@pytest.fixture
def test_task_repository(test_db) -> TaskRepository:
    """Фикстура тестового task_repository"""
    db = test_db
    return TaskRepository(db)


@pytest.fixture
def test_task_service(test_db) -> TaskService:
    """Фикстура тестового task_service. Кэш обязательно мокается отдельно внутри тестов"""
    return TaskService(db=test_db)


@pytest.fixture
def create_start_task(test_task_repository) -> TaskORM:
    """Фикстура для создания стартовой задачи"""
    task = test_task_repository.create(title='Стартовая задача')

    test_task_repository.db.flush()

    return task


@pytest.fixture
def test_client(mock_task_service) -> Generator[TestClient, None, None]:
    """Фикстура для обрезания сервиса для API тестов task"""
    app.dependency_overrides[get_task_service] = lambda: mock_task_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
