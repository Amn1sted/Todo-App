from sqlalchemy.orm import Session
from app.repositories.task import TaskRepository
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema
from app.core.config import get_settings
from app.cache.redis import RedisCacheBackend

settings = get_settings()

class TaskNotFound(Exception):
    """Задача не найдена"""


class TaskService:


    def __init__(self, db: Session) -> None:
        
        self.db = db
        self.task_repository = TaskRepository(db)
        self.cache = RedisCacheBackend(settings.REDIS_URL, settings.CACHE_TTL_SECONDS)


    def list_tasks(self) -> list[TaskSchema]:
        """Получение списка задач"""

        # Получение задачи из кэша, если она в нём имеется
        cached_tasks = self.cache.get(settings.CACHE_TASKS_KEY)
        if cached_tasks is not None:
            tasks = [TaskSchema.model_validate(task) for task in cached_tasks]
            return tasks

        tasks_orm = self.task_repository.get_all()

        task_read = [TaskSchema.model_validate(task) for task in tasks_orm]
        tasks_for_cache = [task.model_dump() for task in task_read]

        # Добавление задач в кэш
        self.cache.set(settings.CACHE_TASKS_KEY, tasks_for_cache)

        return task_read
    

    def create_task(self, task_create: TaskCreateSchema) -> TaskSchema:
        """Создание задачи"""

        # Инвалидируем кэш
        self.cache.delete(settings.CACHE_TASKS_KEY)

        task_orm = self.task_repository.create(title=task_create.title)
        self.db.commit()
        self.db.refresh(task_orm)
        return TaskSchema.model_validate(task_orm)


    def update_task(self, task_id: str, task_update: TaskUpdateSchema) -> TaskSchema:
        """Обновление задачи"""

        # Инвалидируем кэш
        self.cache.delete(settings.CACHE_TASKS_KEY)

        task_for_update = self.task_repository.get_by_id(task_id=task_id)
        if task_for_update is None:
            raise TaskNotFound(f'Задача с id {task_id} не найдена')
        
        if task_update.title:
            task_for_update.title = task_update.title
        if task_update.completed != None:
            task_for_update.completed = task_update.completed
    
        self.db.commit()
        self.db.refresh(task_for_update)
        return TaskSchema.model_validate(task_for_update)
    

    def delete_task(self, task_id: str) -> None:
        """Удаление задачи"""
        
        # Инвалидируем кэш
        self.cache.delete(settings.CACHE_TASKS_KEY)

        task_for_delete = self.task_repository.get_by_id(task_id=task_id)
        if task_for_delete is None:
            raise TaskNotFound(f'Задача с id {task_id} не найдена')
        
        self.task_repository.delete(task=task_for_delete)
        self.db.commit()
