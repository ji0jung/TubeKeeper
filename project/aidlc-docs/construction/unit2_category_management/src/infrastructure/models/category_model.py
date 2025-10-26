from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base
from ...domain.value_objects.category_type import CategoryTypeEnum

class CategoryModel(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(10), nullable=False)
    category_type = Column(SQLEnum(CategoryTypeEnum), nullable=False, default=CategoryTypeEnum.REGULAR)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    hierarchy_level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 자기 참조 관계
    children = relationship("CategoryModel", backref="parent", remote_side=[id])
