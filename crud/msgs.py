from sqlalchemy.orm import Session

from models import users_msgs
from schemas import msgs


def get_msgs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(users_msgs.Msg).offset(skip).limit(limit).all()


def create_user_msgs(db: Session, msg: msgs.MsgCreate, user_id: int):
    db_msg = users_msgs.Msg(**msg.model_dump(), owner_id=user_id)
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

def create_ai_msgs(db: Session, ai_msg: msgs.MsgCreate, user_id: int):
    db_msg = users_msgs.Msg(**ai_msg, owner_id=user_id)
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg
