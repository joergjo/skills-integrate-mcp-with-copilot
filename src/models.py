"""
Database models for the High School Management System

This module defines the SQLAlchemy models for activities and participants.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

Base = declarative_base()

# Association table for many-to-many relationship between activities and participants
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id')),
    Column('participant_id', Integer, ForeignKey('participants.id'))
)

class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    
    # Many-to-many relationship with participants
    participants = relationship(
        "Participant", 
        secondary=activity_participants, 
        back_populates="activities",
        lazy="selectin"  # Use selectin for async compatibility
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants]
        }

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    
    # Many-to-many relationship with activities
    activities = relationship(
        "Activity", 
        secondary=activity_participants, 
        back_populates="participants",
        lazy="selectin"  # Use selectin for async compatibility
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "activities": [a.name for a in self.activities]
        }