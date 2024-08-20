from sqlalchemy.orm import Session

from schemas.prompts import Prompt, PromptCreate
from models import users_msgs



# 获取所有prompts
def get_prompts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(users_msgs.Prompt).offset(skip).limit(limit).all()

#获取特定的prompt
def get_admin_prompt(db: Session, prompt_id:int):
    p = db.query(users_msgs.Prompt).filter(users_msgs.Prompt.id == prompt_id).first()
    return p

def get_prompt_by_category(db: Session, category:str):
    return db.query(users_msgs.Prompt).filter(users_msgs.Prompt.category == category).first()

# 创建新的prompts
def create_admin_prompt(db: Session, prompt:PromptCreate):
    db_prompt = users_msgs.Prompt(**prompt.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

# 更改prompts
def update_admin_prompt(db: Session,prompt:str, prompt_id:int):
    p = db.query(users_msgs.Prompt).filter(users_msgs.Prompt.id == prompt_id).first()
    if(p):
        p.prompt = prompt
    db.commit()
    return p

# 删除prompts
def delete_admin_prompt(db: Session, prompt_id:int):

    db.query(users_msgs.Prompt).filter(users_msgs.Prompt.id == prompt_id).delete()
    db.commit()