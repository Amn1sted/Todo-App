import pytest

from app.db.session import TestSessionlocal
from app.models.base import Base
from app.db.session import test_engine


@pytest.fixture(scope='function')
def test_db():
    """Фикстура для подлючения к бд и её очистки после теста"""
    session = TestSessionlocal()
    session.begin_nested()

    yield session

    session.rollback()
    session.close()

@pytest.fixture(scope='session', autouse=True)
def create_test_tables():
    """Создаём все таблицы в тестовой БД перед запуском тестов"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)