import pytest
from unittest.mock import MagicMock
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema
from app.services.task import TaskNotFound
from app.models.task import TaskORM
from app.core.config import get_settings
from app.services.task import TaskService


settings = get_settings()


def test_list_tasks_returns_cache(test_task_service) -> None:
    """Тестирование получение списка задач при наличии данных в кэше"""
    cached = [
        {
            'id': '1',
            'title': 'Тестовая задача',
            'completed': False
        }
    ]

    test_task_service.cache.get = MagicMock(return_value=cached)
    test_task_service.cache.set = MagicMock()
    test_task_service.task_repository.get_all = MagicMock()

    result = test_task_service.list_tasks()

    assert result == [
        TaskSchema(
            id='1',
            title='Тестовая задача',
            completed=False
        )
    ]

    test_task_service.cache.get.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.task_repository.get_all.assert_not_called()
    test_task_service.cache.set.assert_not_called()


def test_list_tasks_no_cache(test_task_service) -> None:
    """Тестирование возвращения списка задач при пустом кэше"""
    task_orm = TaskORM(id='1', title='Тестовая задача', completed=False)

    test_task_service.cache.get = MagicMock(return_value=None)
    test_task_service.cache.set = MagicMock()
    test_task_service.task_repository.get_all = MagicMock(return_value=[task_orm])

    result = test_task_service.list_tasks()

    assert result == [
        TaskSchema(
            id='1',
            title='Тестовая задача',
            completed=False
        )
    ]
    
    test_task_service.cache.get.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.cache.set.assert_called_once_with(
        settings.CACHE_TASKS_KEY, 
        [
            {
                'id': '1',
                'title': 'Тестовая задача',
                'completed': False
            }
        ]
    )
    test_task_service.task_repository.get_all.assert_called_once()


def test_create_task(test_task_service) -> None:
    """Тестирование создания задачи сервисом"""

    """ORM для мока создания задачи"""
    task_orm = TaskORM(id='1', title='Тестовая задача', completed=False)

    test_task_service.cache.delete = MagicMock()
    test_task_service.task_repository.create = MagicMock(return_value=task_orm)
    test_task_service.db.commit = MagicMock()
    test_task_service.db.refresh = MagicMock()

    task = TaskCreateSchema(title='Тестовая задача')
    result = test_task_service.create_task(task_create=task)

    assert isinstance(result, TaskSchema)
    assert result.id == task_orm.id
    assert result.title == task.title
    assert result.completed == task_orm.completed

    test_task_service.cache.delete.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.task_repository.create.assert_called_once_with(title=task.title)
    test_task_service.db.commit.assert_called_once()
    test_task_service.db.refresh.assert_called_once_with(task_orm)


@pytest.mark.parametrize(
        argnames=['payload', 'expected_title', 'expected_completed'],
        argvalues=[
            [TaskUpdateSchema(title='Обновлённая задача'), 'Обновлённая задача', False], 
            [TaskUpdateSchema(completed=True), 'Стартовая задача', True], 
            [TaskUpdateSchema(title='Обновлённая задача', completed=True), 'Обновлённая задача', True]
        ]
        
)
def test_update_task(
    test_task_service: TaskService, 
    create_start_task: TaskORM, 
    payload: TaskUpdateSchema, 
    expected_title: str, 
    expected_completed: bool
) -> None:
    """Тестирование обновления задачи сервисом"""
    test_task_service.cache.delete = MagicMock()
    test_task_service.task_repository.get_by_id = MagicMock(return_value=create_start_task)
    test_task_service.db.commit = MagicMock()
    test_task_service.db.refresh = MagicMock()

    updated_task = test_task_service.update_task(create_start_task.id, payload)

    assert updated_task.id == create_start_task.id
    assert updated_task.title == expected_title
    assert updated_task.completed == expected_completed
    assert isinstance(updated_task, TaskSchema)

    test_task_service.cache.delete.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.task_repository.get_by_id.assert_called_once_with(task_id=create_start_task.id)
    test_task_service.db.commit.assert_called_once()
    test_task_service.db.refresh.assert_called_once_with(create_start_task)


def test_update_task_not_found(test_task_service) -> None:
    """Тестирование обновления, если задача не найдена"""
    test_task_service.cache.delete = MagicMock()
    test_task_service.task_repository.get_by_id = MagicMock(return_value=None)
    test_task_service.db.commit = MagicMock()
    test_task_service.db.refresh = MagicMock()

    with pytest.raises(TaskNotFound):
        test_task_service.update_task(
            task_id='1',
            task_update=TaskUpdateSchema(title='Несуществующая задача')
        )
    
    test_task_service.cache.delete.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.task_repository.get_by_id.assert_called_once_with(task_id='1')
    test_task_service.db.commit.assert_not_called()
    test_task_service.db.refresh.assert_not_called()


def test_delete_task(test_task_service, create_start_task) -> None:
    """Тестирование удаления задачи сервисом"""
    task = create_start_task

    test_task_service.cache.delete = MagicMock()
    test_task_service.task_repository.get_by_id = MagicMock(return_value=task)
    test_task_service.task_repository.delete = MagicMock(return_value=None)
    test_task_service.db.commit = MagicMock()

    result = test_task_service.delete_task(task.id)

    assert result is None

    test_task_service.cache.delete.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.task_repository.get_by_id.assert_called_once_with(task_id=task.id)
    test_task_service.task_repository.delete.assert_called_once_with(task=task)
    test_task_service.db.commit.assert_called_once()


def test_delete_task_not_found(test_task_service) -> None:
    """Тестирование удаления задачи, если она не найдена"""
    test_task_service.cache.delete = MagicMock()
    test_task_service.task_repository.get_by_id = MagicMock(return_value=None)
    test_task_service.task_repository.delete = MagicMock()
    test_task_service.db.commit = MagicMock()

    with pytest.raises(TaskNotFound):
        test_task_service.delete_task(task_id='1')

    test_task_service.cache.delete.assert_called_once_with(settings.CACHE_TASKS_KEY)
    test_task_service.task_repository.get_by_id.assert_called_once_with(task_id='1')
    test_task_service.task_repository.delete.assert_not_called()
    test_task_service.db.commit.assert_not_called()
