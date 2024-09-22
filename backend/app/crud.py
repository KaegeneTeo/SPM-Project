from sqlalchemy.orm import Session
import models, schemas
from werkzeug.security import generate_password_hash, check_password_hash

def get_employees(db: Session):
    return db.query(models.Employee).all()

def create_employee(db: Session, employee: schemas.Employee):
    db_employee = models.Employee(**employee.model_dump(exclude=['password']))
    if db.query(models.Employee).filter(models.Employee.email == db_employee.email).first() is not None:
        return None
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def get_employee_by_name(db: Session, name: str):
    db_employee = db.query(models.Employee).filter(models.Employee.name == name).first()
    if db_employee is None:
        return None
    return db_employee

# Retrieve all staff by team from Team table
# Can use for viewing schedules/requests for only members of your team (filtered by Team_ID = Current logged in user's Team_ID)
# Possible logic: Store user's Team_ID as a session variable upon login using localStorage.setItem
def get_staff_ids_by_team(db: Session, team_id: int):
    staff_ids = db.query(models.Team.Staff_ID).filter(models.Team.Team_ID == team_id).all()
    return [staff_id[0] for staff_id in staff_ids]


def check_password(self, password):
    return check_password_hash(self.password_hash, password)

