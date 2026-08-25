from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="owned_events")
    staffs = relationship(
        "EventStaff", back_populates="event", cascade="all, delete-orphan")
    tasks = relationship("EventTask", back_populates="event",
                         cascade="all, delete-orphan")


class EventStaff(Base):
    __tablename__ = "event_staff"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(20), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="staffs")
    user = relationship("User", back_populates="event_staffs")
