from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# Models for SQLAlchemy DB. See schemas.py for JSON Input / Output data validation.

class User(Base):
    __tablename__ = "users"

    # Standard User Fields
    id = Column(Integer, primary_key = True, index = True)
    username= Column(String(255), index = True)
    email = Column(String(255), unique = True, nullable = False)
    hashed_password = Column(String(255), nullable = False)
    role = Column(String(255))

    deleted = Column(Boolean, default = False, nullable = False)
    created_at = Column(DateTime, nullable = False, server_default = func.now())

    # Case-specific fields

    # Relationships
    # parent_id = Column(Integer, ForeignKey('parent.id', ondelete = 'CASCADE'))
    # parent = relationship("Parent", back_populates = "user")#, secondary = "mapping_table") # mapping_table for many-to-many
    # children = relationship("Child", back_populates = "user")#, secondary = "mapping_table") # mapping_table for many-to-many