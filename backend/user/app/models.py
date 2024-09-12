from sqlalchemy import Column, Integer, TIMESTAMP, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    password_hash = Column(String(64), nullable=False)
    telegram_id = Column(String(64), nullable=True)
    telegram_tag = Column(String(64), nullable=True)
    image = Column(String(256), nullable=True)

  

