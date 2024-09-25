
from dotenv import load_dotenv
#load_dotenv()
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# dbURL = 'mysql+mysqlconnector://admin:#ZD6mi7nvT#BBK@spmdb.c5okg8oqe41e.us-east-1.rds.amazonaws.com:3306/HRMS'  #rdslink
#dbURL = 'mysql+mysqlconnector://root@localhost:3306/hrms'
#dbURL = 'mysql+mysqlconnector://admin:#ZD6mi7nvT#BBK@spmdb.c5okg8oqe41e.us-east-1.rds.amazonaws.com:3306/HRMS'
dbURL = 'mysql+mysqlconnector://root:root@localhost:8889/hrms'
engine = create_engine(dbURL, echo=True)  #changed back to DATABASE_URL if needed

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
