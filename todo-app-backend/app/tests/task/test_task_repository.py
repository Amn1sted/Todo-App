import pytest
from app.models.task import TaskORM


def test_create_task(test_task_repository) -> None:
    """Тестирование добавления задачи в бд"""
    task = test_task_repository.create(title='Тестовая задача')
    test_task_repository.db.flush()

    # Сбрасываем identity map, чтобы перечитать данные именно из БД
    test_task_repository.db.expire_all()

    task_from_db = test_task_repository.db.get(TaskORM, task.id)

    assert task.id is not None
    assert task_from_db is not None
    assert task_from_db.id == task.id
    assert task_from_db.title == task.title
    assert task_from_db.completed == False


def test_get_all_tasks(test_task_repository) -> None:
    """Тестирование получения списка задач из бд"""
    task1 = test_task_repository.create(title='Новая задача 1')
    task2 = test_task_repository.create(title='Новая задача 2')
    test_task_repository.db.flush()

    tasks_list = test_task_repository.get_all()

    assert len(tasks_list) == 2
    assert {task.id for task in tasks_list} == {task1.id, task2.id}
    assert [task.title for task in tasks_list] == [task1.title, task2.title] 
    assert [task.completed for task in tasks_list] == [task1.completed, task2.completed] 


def test_get_by_id(test_task_repository) -> None:
    """Тестирование получения задачи по id из бд"""
    task1 = test_task_repository.create(title='Новая задача 1')
    task2 = test_task_repository.create(title='Новая задача 2')
    test_task_repository.db.flush()

    task_by_id = test_task_repository.get_by_id(task_id=task2.id)

    assert task_by_id is not None
    assert task_by_id.id == task2.id
    assert task_by_id.title == task2.title
    assert task_by_id.completed == task2.completed


def test_get_by_id_not_found(test_task_repository) -> None:
    """Тестирование получения несуществующей задачи из бд по id"""
    result = test_task_repository.get_by_id(task_id='1')

    assert result is None


def test_delete(test_task_repository) -> None:
    """Тестирование удаления задачи из бд"""
    task1 = test_task_repository.create(title='Ложная задача')
    task2 = test_task_repository.create(title='Задача для удаления')
    test_task_repository.db.flush()

    test_task_repository.delete(task=task2)
    test_task_repository.db.flush()

    tasks_list = test_task_repository.get_all()
    assert len(tasks_list) == 1
    assert tasks_list[0].id == task1.id
    assert test_task_repository.get_by_id(task_id=task2.id) is None


