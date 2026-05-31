from sqlalchemy.orm import Mapped
from app.models.base import Base


class CategoryORM(Base):
    __tablename__ = 'category'
    name: Mapped[str]