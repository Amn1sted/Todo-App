import pytest

from fastapi.testclient import TestClient
from app.schemas.category import CategorySchema, CategoryCreateSchema, CategoryUpdateSchema
from app.services.category import CategoryService
from fastapi import status
from app.api.routers.category import CategoryNotFound


def test_read_category(
    test_client: TestClient, 
    mock_category_service: CategoryService
) -> None:
    """Тестирование метода get в category_router"""
    expected_categories = [
        CategorySchema(
            id='1',
            name='Ожидаемая категория 1',
        ),
        CategorySchema(
            id='2',
            name='Ожидаемая категория 2',
        ),
    ]

    mock_category_service.list_categories.return_value = expected_categories

    response = test_client.get('/categories')

    assert response.status_code == 200
    assert response.json() == [category.model_dump(mode='json') for category in expected_categories]
    
    mock_category_service.list_categories.assert_called_once()


def test_create_category(
    test_client: TestClient, 
    mock_category_service: CategoryService
) -> None:
    """Тестирование метода post в category_router"""
    payload_category = CategoryCreateSchema(name='Ожидаемая категория')
    expected_category = CategorySchema(id='1', name='Ожидаемая категория')

    mock_category_service.create_category.return_value = expected_category

    response = test_client.post('/categories', json=payload_category.model_dump(mode='json'))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_category.model_dump(mode='json')

    mock_category_service.create_category.assert_called_once_with(
        category_create=payload_category
    )


def test_update_category_found(
    test_client: TestClient, 
    mock_category_service: CategoryService
) -> None:
    """Тестирование метода patch в category_router, если категория найдена"""
    category_id = '1'
    test_payload = CategoryUpdateSchema(name='Обновлённая категория')
    expected_category = CategorySchema(id=category_id, name=test_payload.name)
    mock_category_service.update_category.return_value = expected_category

    response = test_client.patch(
        f'/categories/{category_id}', 
        json=test_payload.model_dump(mode='json')
    )
    
    assert response.status_code == 200
    assert response.json() == expected_category.model_dump(mode='json')
    
    mock_category_service.update_category.assert_called_once_with(
        category_id=category_id, 
        category_update=test_payload
    )


def test_update_category_not_found(
    test_client: TestClient, 
    mock_category_service: CategoryService
) -> None:
    """Тестирование метода patch в category_router, если категория не найдена"""
    category_id = '1'
    payload_category = CategoryUpdateSchema(name='Обновлённая категория')

    mock_category_service.update_category.side_effect = CategoryNotFound

    response = test_client.patch(
        f'/categories/{category_id}', 
        json=payload_category.model_dump(mode='json')
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Category not found'

    mock_category_service.update_category.assert_called_once_with(
        category_id=category_id, 
        category_update=payload_category
    )


def test_delete_category_found(
    test_client: TestClient, 
    mock_category_service: CategoryService
) -> None:
    """Тестирование метода delete в category_router, если категория найдена"""
    category_id = '1'
    mock_category_service.delete_category.return_value = None

    response = test_client.delete(f'/categories/{category_id}')
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b''

    mock_category_service.delete_category.assert_called_once_with(category_id=category_id)


def test_delete_category_not_found(
    test_client: TestClient, 
    mock_category_service: CategoryService
) -> None:
    """Тестирование метода delete в category_router, если категория не найдена"""
    category_id = '1'
    mock_category_service.delete_category.side_effect = CategoryNotFound

    response = test_client.delete(f'/categories/{category_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Category not found'

    mock_category_service.delete_category.assert_called_once_with(category_id=category_id)

