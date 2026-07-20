from sqlalchemy.orm import Session
from app.repositories.category import CategoryRepository
from app.schemas.category import CategorySchema, CategoryCreateSchema, CategoryUpdateSchema
from app.cache.redis import RedisCacheBackend
from app.core.config import get_settings


settings = get_settings()


class CategoryNotFound(Exception):
    "Категория не найдена"


class CategoryService:


    def __init__(self, db: Session) -> None:
        self.db = db
        self.category_repository = CategoryRepository(db)
        self.cache = RedisCacheBackend(settings.REDIS_URL, settings.CACHE_TTL_SECONDS)


    def list_categories(self) -> list[CategorySchema]:
        """Получение списка категорий"""

        # Получение категории из кэша, если она в нём имеется
        cached_categories = self.cache.get(settings.CACHE_CATEGORIES_KEY)
        if cached_categories is not None:
            categories = [CategorySchema.model_validate(category) for category in cached_categories]
            return categories

        categories_orm = self.category_repository.get_all()

        category_read = [CategorySchema.model_validate(category) for category in categories_orm]
        categories_for_cache = [category.model_dump() for category in category_read]

        # Добавление категорий в кэш
        self.cache.set(settings.CACHE_CATEGORIES_KEY, categories_for_cache)

        return category_read
    

    def create_category(self, category_create: CategoryCreateSchema) -> CategorySchema:
        """Создание категории"""

        # Инвалидируем кэш
        self.cache.delete(settings.CACHE_CATEGORIES_KEY)

        category_orm = self.category_repository.create(name=category_create.name)
        self.db.commit()
        self.db.refresh(category_orm)
        return CategorySchema.model_validate(category_orm)


    def update_category(self, category_id: str, category_update: CategoryUpdateSchema) -> CategorySchema:
        """Обновление категории"""

        # Инвалидируем кэш
        self.cache.delete(settings.CACHE_CATEGORIES_KEY)

        category_for_update = self.category_repository.get_by_id(category_id=category_id)
        if category_for_update is None:
            raise CategoryNotFound(f'Категория с id {category_id} не найдена')

        if category_update.name:
            category_for_update.name = category_update.name
        
        self.db.commit()
        self.db.refresh(category_for_update)

        return CategorySchema.model_validate(category_for_update)


    def delete_category(self, category_id: str) -> None:
        """Удаление категории"""

        # Инвалидируем кэш
        self.cache.delete(settings.CACHE_CATEGORIES_KEY)

        category_for_delete = self.category_repository.get_by_id(category_id=category_id)

        if category_for_delete is None:
            raise CategoryNotFound(f'Категория с id {category_id} не найдена')
        
        self.category_repository.delete(category=category_for_delete)
        self.db.commit()