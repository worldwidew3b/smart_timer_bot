from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


# Association table for many-to-many relationship between tasks and tags
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tasks = relationship("Task", back_populates="user")
    tags = relationship("Tag", back_populates="user")


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    color = Column(String, nullable=True)  # Color code for UI
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationship
    user = relationship("User", back_populates="tags")
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    estimated_time = Column(Integer)  # Estimated time in minutes
    priority = Column(Integer, default=1)  # Priority level 1-5
    user_id = Column(Integer, ForeignKey('users.id'))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    actual_time_spent = Column(Integer, default=0)  # Actual time spent in minutes

    # Relationships
    user = relationship("User", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")
    timer_sessions = relationship("TimerSession", back_populates="task")
    completions = relationship("TaskCompletion", back_populates="task")


class TimerSession(Base):
    __tablename__ = 'timer_sessions'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    active = Column(Boolean, default=True)

    # Relationship
    task = relationship("Task", back_populates="timer_sessions")


class TaskCompletion(Base):
    __tablename__ = 'task_completions'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    actual_time_spent = Column(Integer)  # Time spent on this completion in minutes

    # Relationship
    task = relationship("Task", back_populates="completions")