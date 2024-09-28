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

# Retrieve all Team_IDs that the logged-in user belongs to
def get_team_ids(db: Session, staff_id: int):
    team_ids = db.query(models.Team.team_id).filter(models.Team.staff_id == staff_id).all()
    return [team_id[0] for team_id in team_ids]

# Retrieve all staff by team(s) from Team table
# Can use for viewing schedules/requests for only members of your team(s) (filtered by Team_ID = Current logged in user's Team_ID(s))
def get_staff_ids_by_team(db: Session, team_ids: list[int]):
    if not team_ids:
        return []
    # Query staff IDs from team ID(s)
    staff_ids = db.query(models.Team.staff_id).filter(models.Team.team_id.in_(team_ids)).all()
    return [staff_id[0] for staff_id in staff_ids]

# Retrieve all requests from staff members in the list of staff_ids
def get_requests_by_staff_ids(db: Session, staff_ids: list[int]):
    if not staff_ids:
        return []
    requests = db.query(models.Request).filter(models.Request.staff_id.in_(staff_ids)).all()
    return requests

# Retrieve the selected request by request_id
def get_request_by_id(db: Session, request_id: int):
    request = db.query(models.Request).filter(models.Request.request_id == request_id).first()
    return request

# Method executed upon clicking 'Approve' button
def approve_request(db: Session, request_id: int):
    request = db.query(models.Request).filter(models.Request.request_id == request_id).first()
    if request:
        request.status = 1
        db.commit()
        db.refresh(request)
    return request

# Method executed upon clicking 'Reject' button
def reject_request(db: Session, request_id: int):
    request = db.query(models.Request).filter(models.Request.request_id == request_id).first()
    if request:
        request.status = -1
        db.commit()
        db.refresh(request)
    return request

# Retrieve requests from a specific staff_id
def get_request(db:Session, staff_id:int):
    requests = db.query(models.Request).filter(models.Request.staff_id == staff_id).all()
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
    models.Employee.staff_id == staff_id
    ).all()
    return results

