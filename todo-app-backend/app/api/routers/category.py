from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.category import CategorySchema, UpdateCategorySchema, CreateCategorySchema
from app.services.category import CategoryService
from app.api.dependencies import get_category_service
from app.services.category import CategoryNotFound


category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('')
def read_categories(category_service: CategoryService = Depends(get_category_service)) -> list[CategorySchema]:
    return category_service.list_categories()


@category_router.post('', status_code=status.HTTP_201_CREATED)
def create_category(payload: CreateCategorySchema, category_service: CategoryService = Depends(get_category_service)) -> CategorySchema:
    return category_service.create_category(category_create=payload)


@category_router.patch('/{category_id}')
def update_category(payload: UpdateCategorySchema, category_id: str, category_service: CategoryService = Depends(get_category_service)) -> CategorySchema:
    try:
        return category_service.update_category(category_id=category_id, category_update=payload)          
    except CategoryNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
        

@category_router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, category_service: CategoryService = Depends(get_category_service)):
    try:
        return category_service.delete_category(category_id=category_id)
    except CategoryNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
