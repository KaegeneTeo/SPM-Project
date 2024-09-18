
from dotenv import load_dotenv
#load_dotenv()
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

dbURL = 'mysql+mysqlconnector://root@localhost:3306/hrms'
 
engine = create_engine(dbURL, echo=True)  #changed back to DATABASE_URL if needed

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()