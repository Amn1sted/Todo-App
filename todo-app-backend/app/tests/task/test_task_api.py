import pytest
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema
import json
from app.services.task import TaskService, TaskNotFound
from fastapi.testclient import TestClient
from fastapi import status


def test_read_task(test_client: TestClient, mock_task_service: TaskService):
    """Тестирование метода get в task_router"""
    expected_tasks = [
        TaskSchema(
            id='1',
            title='Ожидаемая задача 1',
            completed=False
        ),
        TaskSchema(
            id='2',
            title='Ожидаемая задача 2',
            completed=True
        ),
    ]

    mock_task_service.list_tasks.return_value = expected_tasks

    response = test_client.get('/tasks')

    assert response.status_code == 200
    assert response.json() == [task.model_dump(mode='json') for task in expected_tasks]
    
    mock_task_service.list_tasks.assert_called_once()


def test_create_task(test_client: TestClient, mock_task_service: TaskService):
    """Тестирование метода post в task_router"""
    payload_task = TaskCreateSchema(title='Ожидаемая задача')
    expected_task = TaskSchema(id='1', title='Ожидаемая задача', completed=False)

    mock_task_service.create_task.return_value = expected_task

    response = test_client.post('/tasks', json=payload_task.model_dump(mode='json'))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_task.model_dump(mode='json')

    mock_task_service.create_task.assert_called_once_with(task_create=payload_task)


@pytest.mark.parametrize(
        argnames=['payload', 'expected_title', 'expected_completed'],
        argvalues=[
            [TaskUpdateSchema(title='Обновлённая задача'), 'Обновлённая задача', False],
            [TaskUpdateSchema(completed=True), 'Стартовая задача', True],
            [TaskUpdateSchema(title='Обновлённая задача', completed=True), 'Обновлённая задача', True]
    ]
)
def test_update_task_found(
    test_client: TestClient,
    mock_task_service: TaskService,
    payload: TaskUpdateSchema,
    expected_title: str,
    expected_completed: bool
):
    """Тестирование метода patch в task_router, если задача найдена"""
    task_id = '1'
    expected_task = TaskSchema(id=task_id, title=expected_title, completed=expected_completed)
    mock_task_service.update_task.return_value = expected_task

    response = test_client.patch(
        f'/tasks/{task_id}', 
        json=payload.model_dump(mode='json', exclude_unset=True)
    )
    
    assert response.status_code == 200
    assert response.json() == expected_task.model_dump(mode='json')
    
    mock_task_service.update_task.assert_called_once_with(task_id=task_id, task_update=payload)


def test_update_task_not_found(test_client: TestClient, mock_task_service: TaskService):
    """Тестирование метода patch в task_router, если задача не найдена"""
    task_id = '1'
    payload_task = TaskUpdateSchema(title='Обновлённая задача', completed=False)

    mock_task_service.update_task.side_effect = TaskNotFound

    response = test_client.patch(
        f'/tasks/{task_id}', 
        json=payload_task.model_dump(mode='json', exclude_unset=True)
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'

    mock_task_service.update_task.assert_called_once_with(task_id=task_id, task_update=payload_task)


def test_delete_task_found(test_client: TestClient, mock_task_service: TaskService):
    """Тестирование метода delete в task_router, если задача найдена"""
    task_id = '1'
    mock_task_service.delete_task.return_value = None

    response = test_client.delete(f'/tasks/{task_id}')
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''

    mock_task_service.delete_task.assert_called_once_with(task_id=task_id)


def test_delete_task_not_found(test_client: TestClient, mock_task_service: TaskService):
    """Тестирование метода delete в task_router, если задача не найдена"""
    task_id = '1'
    mock_task_service.delete_task.side_effect = TaskNotFound

    response = test_client.delete(f'/tasks/{task_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'

    mock_task_service.delete_task.assert_called_once_with(task_id=task_id)