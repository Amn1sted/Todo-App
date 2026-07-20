from fastapi import Depends
from app.services.task import TaskService
from app.services.category import CategoryService
from sqlalchemy.orm import Session
from app.db.session import get_db


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    "Функция для инъекции зависимости TaskService"
    return TaskService(db)

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    "Функция для инъекции зависимости CategoryService"
    return CategoryService(db)