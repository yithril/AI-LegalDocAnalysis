from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class UserUserGroup(Base):
    """Many-to-many relationship between users and user groups"""
    __tablename__ = 'user_user_groups'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user_group_id = Column(Integer, ForeignKey('user_groups.id'), primary_key=True)
    
    # Relationships
    user = relationship("User", back_populates="user_groups")
    user_group = relationship("UserGroup", back_populates="users")
    
    def __repr__(self):
        return f"<UserUserGroup(user_id={self.user_id}, user_group_id={self.user_group_id})>" 