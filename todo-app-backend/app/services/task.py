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
        self.cache = RedisCacheBackend(settings.redis_url, settings.cache_ttl_seconds)

    def list_tasks(self) -> list[TaskSchema]:
        cached_tasks = self.cache.get(settings.cache_tasks_key)
        if cached_tasks is not None:
            return cached_tasks

        tasks_orm = self.task_repository.get_all()

        task_read = [TaskSchema.model_validate(task) for task in tasks_orm]
        tasks_for_cache = [task.model_dump() for task in task_read]
        self.cache.set(settings.cache_tasks_key, tasks_for_cache)

        return task_read
    
    def create_task(self, task_create: TaskCreateSchema) -> TaskSchema: 
        self.cache.delete(settings.cache_tasks_key)

        task_orm = self.task_repository.create(title=task_create.title)
        self.db.commit()
        return TaskSchema.model_validate(task_orm)

    def update_task(self, task_id: str, task_update: TaskUpdateSchema) -> TaskSchema:
        self.cache.delete(settings.cache_tasks_key)

        task_for_update = self.task_repository.get_by_id(task_id=task_id)
        if task_for_update is None:
            raise TaskNotFound(f'Задача с id {task_id} не найдена')
        
        if task_update.title:
            task_for_update.title = task_update.title
        if task_update.completed != None:
            task_for_update.completed = task_update.completed
    
        self.db.commit()
        return TaskSchema.model_validate(task_for_update)
    
    def delete_task(self, task_id: str) -> None:
        self.cache.delete(settings.cache_tasks_key)

        task_for_delete = self.task_repository.get_by_id(task_id)
        if task_for_delete is None:
            raise TaskNotFound(f'Задача с id {task_id} не найдена')
        
        self.task_repository.delete(task_for_delete)
        self.db.commit()
