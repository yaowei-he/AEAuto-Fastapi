from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from schemas.users import User, UserCreate
from crud.users import (get_user_by_username, 
    get_user, get_users, create_user,admin_user, 
    get_current_active_user, level_user)
from db.database import get_db
from pathlib import Path

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


VIDEO_PATH = Path("static/test.mp4")
@router.get("/stream-video")
async def stream_hls():
    def generate():
        with open(VIDEO_PATH, "rb") as video_file:
            while True:
                chunk = video_file.read(1024)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(generate(), media_type="video/mp4")


# 用户新建
@router.post("/", response_model=User)
def router_create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已被注册")
    return create_user(db=db, user=user)


# 用户信息
@router.get("/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


# 搜索其他用户
@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# 自己
@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/admin/{user_id}", response_model=User)
async def admin_users_(
    user_id: int, db: Session = Depends(get_db)
):
    
    return admin_user(db,user_id)


# 获取用户等级
@router.get("/{user_id}/level", response_model=User)
async def level_users(
    user_id: int, db: Session = Depends(get_db)
):
    
    return level_user(db,user_id)


# # 获取用户使用量
# @router.get("/{user_id}/usage", response_model=User)
# async def usage_users(
#     user_id: int, db: Session = Depends(get_db)
# ):
    
#     return level_user(db,user_id)
