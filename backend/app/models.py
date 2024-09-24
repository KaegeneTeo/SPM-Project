from sqlalchemy import Column, Integer, TIMESTAMP, String, ForeignKey, Date
from sqlalchemy.orm import relationship, sessionmaker
from database import Base

class Employee(Base):
    __tablename__ = 'employee'
    staff_id = Column(Integer, primary_key=True)
    staff_fname = Column(String(64), nullable=False)
    staff_lname = Column(String(64), nullable=False)
    dept = Column(String(64), nullable=True)
    position = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    email = Column(String(256), nullable=False)
    reporting_manager = Column(Integer, ForeignKey("employee.staff_id"), nullable=False)
    role = Column(Integer, nullable=False)
    password_hash = Column(String(256), nullable=False)
    schedule = relationship("schedule", back_populates="employee")
    
  
class Schedule(Base):
    __tablename__ = 'schedule'
    schedule_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey("employee.staff_id"), nullable=False)
    date = Column(Date, nullable=False)
    time_slot = Column(Integer, nullable=False)
    employee = relationship("employee", back_populates="schedule")

    


class Team(Base):
    __tablename__ = 'team'
    team_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey("employee.staff_id"), primary_key=True)

class Request(Base):
    __tablename__ = "request"
    request_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey("employee.staff_id"),nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedule.schedule_id"), nullable = False)
    reason = Column(String(200), nullable=False)
    status = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    time_slot = Column(Integer, nullable=False)
    request_type = Column(Integer, nullable=False)