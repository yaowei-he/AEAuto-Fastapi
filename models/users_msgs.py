from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    level = Column(String, default="1")
   
    # 账号是否被冻结
    is_active = Column(Boolean, default=True)
    # 是否为管理员
    is_admin = Column(Boolean, default=False)
    
    # 使用限制 和USER对应
    max_usage = Column(Integer,default=100)

    # 当前使用量
    current_usage = Column(Integer,default=0)

    msgs = relationship("Msg", back_populates="owner")


class Msg(Base):
    __tablename__ = "msgs"

    id = Column(Integer, primary_key=True)
    # 类型
    category = Column(String, index=True)
    # 时间
    time = Column(String)
    # 角色内容
    content = Column(String)
    
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="msgs")

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True)

    # 类别
    category = Column(String, index=True)

    #系统提示词
    prompt = Column(String)

    #统计使用次数
    count = Column(String, default=0)
