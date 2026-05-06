from sqlalchemy.orm import Session
from app.repositories.category import CategoryRepository
from app.models.category import CategoryORM
from app.schemas.category import CategorySchema, CreateCategorySchema, UpdateCategorySchema


class CategoryNotFound(Exception):
    "Категория не найдена"


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repository = CategoryRepository(db)

    def list_categories(self) -> list[CategoryORM]:
        categories_orm = self.category_repository.get_all()

        return [CategorySchema.model_validate(category) for category in categories_orm]
    
    def create_category(self, category_create: CreateCategorySchema) -> CategorySchema:
        category_orm = self.category_repository.create(name=category_create.name)
        self.db.commit()

        return CategorySchema.model_validate(category_orm)
    
    def update_category(self, category_id: str, category_update: UpdateCategorySchema) -> CategorySchema:
        category_for_update = self.category_repository.get_by_id(category_id=category_id)
        if category_for_update is None:
            raise CategoryNotFound(f'Категория с id {category_id} не найдена')

        if category_for_update.name:
            category_for_update.name = category_update.name
        
        self.db.commit()

        return CategorySchema.model_validate(category_for_update)

    def delete_category(self, category_id: str) -> None:
        category_for_delete = self.category_repository.get_by_id(category_id=category_id)

        if category_for_delete is None:
            raise CategoryNotFound(f'Категория с id {category_id} не найдена')
        
        self.category_repository.delete(category_for_delete)
        self.db.commit()