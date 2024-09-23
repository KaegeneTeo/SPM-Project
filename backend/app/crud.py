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

# Retrieve all staff by team from Team table
# Can use for viewing schedules/requests for only members of your team (filtered by Team_ID = Current logged in user's Team_ID)
# Possible logic: Store user's Team_ID as a session variable upon login using localStorage.setItem
def get_staff_ids_by_team(db: Session, team_id: int):
    staff_ids = db.query(models.Team.Staff_ID).filter(models.Team.Team_ID == team_id).all()
    return [staff_id[0] for staff_id in staff_ids]


# Retrieve all requests from staff members in the list of staff_ids
def get_requests_by_staff_ids(db: Session, staff_ids: list):
    if not staff_ids:
        return []
    requests = db.query(models.Request).filter(models.Request.Staff_ID.in_(staff_ids)).all()
    return requests



def check_password(self, password):
    return check_password_hash(self.password_hash, password)

def get_schedules(db: Session, filters: dict):
    dept = filters.dept
    team = filters.team
    staff_id = filters.staff_id
    results = db.query(models.Employee).join(models.Schedule).filter(
    models.Schedule.status == 1,
    models.Employee.dept == dept,
    models.Employee.team == team,
    models.Employee.Staff_ID == staff_id
    ).all()
    return results

