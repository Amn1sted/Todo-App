import pytest

from app.core.config import get_settings
from unittest.mock import MagicMock
from app.schemas.category import CategorySchema, CategoryCreateSchema, CategoryUpdateSchema
from app.models.category import CategoryORM
from app.services.category import CategoryNotFound

settings = get_settings()

def test_list_categories_returns_cache(test_category_service) -> None:
    """Тестирование получение списка категорий при наличии данных в кэше"""
    cached = [
        {
            'id': '1',
            'name': 'Тестовая категория',
        }
    ]

    test_category_service.cache.get = MagicMock(return_value=cached)
    test_category_service.cache.set = MagicMock()
    test_category_service.category_repository.get_all = MagicMock()

    result = test_category_service.list_categories()

    assert result == [
        CategorySchema(
            id='1',
            name='Тестовая категория',
        )
    ]

    test_category_service.cache.get.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.category_repository.get_all.assert_not_called()
    test_category_service.cache.set.assert_not_called()


def test_list_categories_no_cache(test_category_service) -> None:
    """Тестирование возвращения списка категорий при пустом кэше"""
    category_orm = CategoryORM(id='1', name='Тестовая категория')

    test_category_service.cache.get = MagicMock(return_value=None)
    test_category_service.cache.set = MagicMock()
    test_category_service.category_repository.get_all = MagicMock(return_value=[category_orm])

    result = test_category_service.list_categories()

    assert result == [
        CategorySchema(
            id='1',
            name='Тестовая категория'
        )
    ]
    
    test_category_service.cache.get.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.cache.set.assert_called_once_with(
        settings.CACHE_CATEGORIES_KEY, 
        [
            {
                'id': '1',
                'name': 'Тестовая категория',
            }
        ]
    )
    test_category_service.category_repository.get_all.assert_called_once()


def test_create_category(test_category_service) -> None:
    """Тестирование создания категории сервисом"""

    """ORM для мока создания категории"""
    category_orm = CategoryORM(id='1', name='Тестовая категория')

    test_category_service.cache.delete = MagicMock()
    test_category_service.category_repository.create = MagicMock(return_value=category_orm)
    test_category_service.db.commit = MagicMock()
    test_category_service.db.refresh = MagicMock()

    category = CategoryCreateSchema(name='Тестовая категория')
    result = test_category_service.create_category(category_create=category)

    assert isinstance(result, CategorySchema)
    assert result.id == category_orm.id
    assert result.name == category.name

    test_category_service.cache.delete.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.category_repository.create.assert_called_once_with(name=category.name)
    test_category_service.db.commit.assert_called_once()
    test_category_service.db.refresh.assert_called_once_with(category_orm)


def test_update_category(test_category_service, create_start_category) -> None:
    """Тестирование обновления категории сервисом"""
    test_payload = CategoryUpdateSchema(name='Обновлённая категория')

    test_category_service.cache.delete = MagicMock()
    test_category_service.category_repository.get_by_id = MagicMock(return_value=create_start_category)
    test_category_service.db.commit = MagicMock()
    test_category_service.db.refresh = MagicMock()

    updated_category = test_category_service.update_category(create_start_category.id, test_payload)

    assert updated_category.id == create_start_category.id
    assert updated_category.name == test_payload.name
    assert isinstance(updated_category, CategorySchema)

    test_category_service.cache.delete.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.category_repository.get_by_id.assert_called_once_with(category_id=create_start_category.id)
    test_category_service.db.commit.assert_called_once()
    test_category_service.db.refresh.assert_called_once_with(create_start_category)


def test_update_category_not_found(test_category_service) -> None:
    """Тестирование обновления, если категория не найдена"""
    test_category_service.cache.delete = MagicMock()
    test_category_service.category_repository.get_by_id = MagicMock(return_value=None)
    test_category_service.db.commit = MagicMock()
    test_category_service.db.refresh = MagicMock()

    with pytest.raises(CategoryNotFound):
        test_category_service.update_category(
            category_id='1',
            category_update=CategoryUpdateSchema(name='Несуществующая категория')
        )
    
    test_category_service.cache.delete.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.category_repository.get_by_id.assert_called_once_with(category_id='1')
    test_category_service.db.commit.assert_not_called()
    test_category_service.db.refresh.assert_not_called()


def test_delete_category(test_category_service, create_start_category) -> None:
    """Тестирование удаления категории сервисом"""
    category = create_start_category

    test_category_service.category_repository.get_by_id = MagicMock(return_value=category)
    test_category_service.cache.delete = MagicMock()
    test_category_service.category_repository.delete = MagicMock(return_value=None)
    test_category_service.db.commit = MagicMock()
    result = test_category_service.delete_category(category.id)

    assert result is None

    test_category_service.cache.delete.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.category_repository.get_by_id.assert_called_once_with(category_id=category.id)
    test_category_service.category_repository.delete.assert_called_once_with(category=category)
    test_category_service.db.commit.assert_called_once()


def test_delete_category_not_found(test_category_service) -> None:
    """Тестирование удаления категории, если она не найдена"""
    test_category_service.cache.delete = MagicMock()
    test_category_service.category_repository.get_by_id = MagicMock(return_value=None)
    test_category_service.category_repository.delete = MagicMock()
    test_category_service.db.commit = MagicMock()

    with pytest.raises(CategoryNotFound):
        test_category_service.delete_category(category_id='1')

    test_category_service.cache.delete.assert_called_once_with(settings.CACHE_CATEGORIES_KEY)
    test_category_service.category_repository.get_by_id.assert_called_once_with(category_id='1')
    test_category_service.category_repository.delete.assert_not_called()
    test_category_service.db.commit.assert_not_called()