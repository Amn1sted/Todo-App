from pydantic import BaseModel, ConfigDict


class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class CreateCategorySchema(BaseModel):
    name: str


class UpdateCategorySchema(CreateCategorySchema):
    pass