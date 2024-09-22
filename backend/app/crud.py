from sqlalchemy.orm import Session
import models, schemas
from werkzeug.security import generate_password_hash, check_password_hash

def get_employees(db: Session):
    return db.query(models.Employee).all()

def create_employee(db: Session, employee: schemas.Employee):
    employee.password_hash = generate_password_hash(employee.password, method='pbkdf2:sha256')
    db_employee = models.Employee(**employee.model_dump(exclude=['password']))
    if db.query(models.Employee).filter(models.Employee.email == db_employee.email).first() is not None:
        return None
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def get_employee_by_email(db: Session, email: str):
    db_employee = db.query(models.Employee).filter(models.Employee.email == email).first()
    if db_employee is None:
        return None
    return db_employee


def check_password(self, password):
    return check_password_hash(self.password_hash, password)

