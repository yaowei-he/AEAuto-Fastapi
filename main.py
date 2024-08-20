from datetime import timedelta
from fastapi import Depends, FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import users_msgs
from routers import users, msgs, prompts
from db.database import engine
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.users import Token
from fastapi.security import OAuth2PasswordRequestForm

from db.database import get_db
from crud.users import authenticate_user, create_access_token


users_msgs.Base.metadata.create_all(bind=engine)
# app配置
app = FastAPI(
    title= "FastGPT",

    # 初始版本
    version="0.0.1"
)

from os import environ  # environ 用于获取系统环境变量
from dotenv import load_dotenv 


load_dotenv()
ACCESS_TOKEN_EXPIRE_WEEKS=environ.get("ACCESS_TOKEN_EXPIRE_WEEKS")


# 跨源处理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_ip_address(request: Request, call_next):
    client_host = request.client.host
    print(f"客户端地址: {client_host}")

    # 写入日志或者记事本
    response = await call_next(request)
    return response

app.include_router(users.router)
app.include_router(msgs.router)
app.include_router(prompts.router)

# 测试用
@app.get("/")
def read_root():
    return {"hello": "World"}

# 用户token
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:Session=Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码或者用户名错误!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(weeks=float(ACCESS_TOKEN_EXPIRE_WEEKS))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

# minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)