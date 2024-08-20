from sqlalchemy.orm import Session
from typing import Annotated

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from models.users_msgs import User
from schemas.users import UserCreate, TokenData
from datetime import datetime, timedelta, timezone
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from db.database import get_db
from os import environ  # environ 用于获取系统环境变量
from dotenv import load_dotenv 


load_dotenv()

SECRET_KEY=environ.get("SECRET_KEY")
ALGORITHM=environ.get("ALGORITHM")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 获取用户信息
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_password_hash(password):
    return pwd_context.hash(password)


# 用户认证
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 用户添加
def create_user(db: Session, user: UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 获取当前用户
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# 获取当前有效用户
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 用户管理员升级
def admin_user(db: Session, user_id: int):
    u = db.query(User).filter(User.id==user_id).first()
    u.is_admin = True
    db.commit()
    return u

# 等级升级
def level_user(db: Session, user_id: int):
    u = db.query(User).filter(User.id==user_id).first()
    curennt_level = int(u.level) + 1
    u.level = str(curennt_level)
    db.commit()
    return u

# 计算使用量
def count_usage(db: Session, user_id: int):
    u = db.query(User).filter(User.id==user_id).first()
    u.current_usage += 1
    db.commit()
    # return u
    