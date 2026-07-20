import pytest

from app.models.category import CategoryORM


def test_create_category(test_category_repository) -> None:
    """Тестирование добавления категории в бд"""
    category = test_category_repository.create(name='Тестовая категория')
    test_category_repository.db.flush()

    # Сбрасываем identity map, чтобы перечитать данные именно из БД
    test_category_repository.db.expire_all()

    category_from_db = test_category_repository.db.get(CategoryORM, category.id)

    assert category.id is not None
    assert category_from_db is not None
    assert category_from_db.id == category.id
    assert category_from_db.name == category.name


def test_get_all_categories(test_category_repository) -> None:
    """Тестирование получения списка категорий из бд"""
    category1 = test_category_repository.create(name='Новая категория 1')
    category2 = test_category_repository.create(name='Новая категория 2')
    test_category_repository.db.flush()

    categories_list = test_category_repository.get_all()

    assert len(categories_list) == 2
    assert {category.id for category in categories_list} == {category1.id, category2.id}
    assert [category.name for category in categories_list] == [category1.name, category2.name] 


def test_get_by_id(test_category_repository) -> None:
    """Тестирование получения категории по id из бд"""
    category1 = test_category_repository.create(name='Ложная категория')
    category2 = test_category_repository.create(name='Нужная категория')
    test_category_repository.db.flush()

    category_by_id = test_category_repository.get_by_id(category_id=category2.id)

    assert category_by_id is not None
    assert category_by_id.id == category2.id
    assert category_by_id.name == category2.name


def test_get_by_id_not_found(test_category_repository) -> None:
    """Тестирование получения несуществующей категории из бд по id"""
    result = test_category_repository.get_by_id(category_id='1')

    assert result is None


def test_delete(test_category_repository) -> None:
    """Тестирование удаления категории из бд"""
    category1 = test_category_repository.create(name='Ложная категория')
    category2 = test_category_repository.create(name='Категория для удаления')
    test_category_repository.db.flush()

    test_category_repository.delete(category=category2)
    test_category_repository.db.flush()

    categories_list = test_category_repository.get_all()
    assert len(categories_list) == 1
    assert categories_list[0].id == category1.id
    assert test_category_repository.get_by_id(category_id=category2.id) is None