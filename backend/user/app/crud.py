from sqlalchemy.orm import Session
import models, schemas
from werkzeug.security import generate_password_hash, check_password_hash

def get_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, user: schemas.User):
    db_user = models.User(**user.model_dump(exclude=['password']))
    if db.query(models.User).filter(models.User.email == db_user.email).first() is not None:
        return None
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        return None
    return db_user

def get_user_by_telegram_tag(db: Session, telegram_tag: str):
    db_user = db.query(models.User).filter(models.User.telegram_tag == telegram_tag).first()
    if db_user is None:
        return None
    return db_user

def update_user(db: Session, user: schemas.User, user_id: int):
    print(user)
   
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        return None

    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
  
    db.commit()
    db.refresh(db_user)
    return db_user



def check_password(self, password):
    return check_password_hash(self.password_hash, password)

def update_user_password(db: Session, user: schemas.User, user_id: int):
   
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        return None

    user.password_hash = generate_password_hash(user.password, method='pbkdf2:sha256')
  
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_user_id(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        return None
    return db_user
