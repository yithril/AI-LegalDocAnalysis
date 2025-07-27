from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class ProjectUserGroup(Base):
    """Many-to-many relationship between projects and user groups"""
    __tablename__ = 'project_user_groups'

    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    user_group_id = Column(Integer, ForeignKey('user_groups.id'), primary_key=True)
    
    # Relationships
    project = relationship("Project", back_populates="project_user_groups")
    user_group = relationship("UserGroup", back_populates="project_user_groups")
    
    def __repr__(self):
        return f"<ProjectUserGroup(project_id={self.project_id}, user_group_id={self.user_group_id})>" 