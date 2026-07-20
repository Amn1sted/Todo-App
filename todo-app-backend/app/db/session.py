from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings


settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)


def get_db():
    """""Функция для инъекции сессии БД"""""
    db = Sessionlocal()

    try:
        yield db
    finally:
        db.close()

test_engine = create_engine(settings.TEST_DATABASE_URL)
TestSessionlocal = sessionmaker(bind=test_engine)

def get_test_db():
    test_db = TestSessionlocal()
    try:
        yield test_db
    finally:
        test_db.close()