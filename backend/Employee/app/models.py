from sqlalchemy import Column, Integer, TIMESTAMP, String
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
    reporting_manager = Column(Integer, nullable=False)
    role = Column(Integer, nullable=False)
  

