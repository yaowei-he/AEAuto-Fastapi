
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.prompts import PromptCreate, Prompt
from db.database import get_db

from crud.prompts import get_admin_prompt, get_prompts, update_admin_prompt, delete_admin_prompt, create_admin_prompt

from crud.users import get_current_active_user, get_user

router = APIRouter(
    prefix="/api/prompts",
    tags=["prompts"],
    dependencies=[Depends(get_current_active_user)]
)

# 获取所有
@router.get("/", response_model=list[Prompt])
def read_all_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prompts = get_prompts(db, skip=skip, limit=limit)
    return prompts

# 添加promopt
@router.post("/", response_model=Prompt)
def add_admin_prompt(
    prompt: PromptCreate, db: Session = Depends(get_db)
):
    return create_admin_prompt(db=db,prompt=prompt)


# 按id获取
@router.get("/{prompt_id}", response_model=Prompt)
def read_prompt(prompt_id: int, db: Session = Depends(get_db)):
    db_prompt = get_admin_prompt(db=db, prompt_id=prompt_id)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


#更新prompt
@router.put('/admin/{prompt_id}', response_model=Prompt)
def update_prompt(prompt_id: int,prompt:str, db: Session = Depends(get_db)):
    #获取原有prompt
    return update_admin_prompt(db,prompt, prompt_id)


#删除prompt
@router.delete('/admin/{prompt_id}')
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    delete_admin_prompt(db,prompt_id)

    return {"progress":"success"}