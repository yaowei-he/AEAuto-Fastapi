from fastapi import APIRouter, Depends, HTTPException, Response, Request
from grpc import Status
from sqlalchemy.orm import Session
from db.database import get_db

from schemas.msgs import Msg, MsgCreate, Out

from crud.users import get_current_active_user, get_user, count_usage
from crud.msgs import create_user_msgs, get_msgs, create_ai_msgs
from crud.prompts import get_prompt_by_category

from fastapi.responses import StreamingResponse
import asyncio
import json

from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.gptsapi.net/v1/")


router = APIRouter(
    prefix="/api/msgs",
    tags=["msgs"],
    dependencies=[Depends(get_current_active_user)]
)


# 发送信息
@router.post("/{user_id}/", response_model=Msg)
def create_msg_for_user(
    user_id: int, msg: MsgCreate, db: Session = Depends(get_db)
):
    return create_user_msgs(db=db, msg=msg, user_id=user_id)
    

# AE表达式
@router.post('/{user_id}/expressions/', response_model=Out)
async def ae_expressions(
    user_id: int, msg: MsgCreate, db: Session = Depends(get_db)
):
    # 获取用户的存量
    user= get_user(db,user_id)
    max = user.max_usage
    current = user.current_usage

    # 为了保险起见在服务端设置一边，主要靠客户端的
    if not user.is_admin:
        if current > max :
            return msg
    #计算用户量
    count_usage(db,user_id)
# 用户存入数据库
    create_user_msgs(db=db, msg=msg, user_id=user_id)
# 提取用户问题
    user_question = msg.content.split("_")[-1]

# 等待chatgpt回答  
    
    sys_prompt = get_prompt_by_category(db=db, category=msg.category).prompt

# 虚拟处理提示词和用户问题
    
    res = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        temperature=0,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_question}
        ])
    ai_res = res.choices[0].message.content

  
    data = json.loads(ai_res)

    ai_code = data["code"]
    ai_explain = data["explain"]

    ai_msg = {
        "time": "2025",
        "category":"expressions",
        "code": ai_code,
        "content":"AI_"+ai_explain,
    }

    return ai_msg



# AE自动化
@router.post('/{user_id}/ae/', response_model=Out)
async def ae_auto(
    user_id: int, msg: MsgCreate, db: Session = Depends(get_db)
):
    
    # 获取用户的存量
    user= get_user(db,user_id)
    max = user.max_usage
    current = user.current_usage

    # 为了保险起见在服务端设置一边，主要靠客户端的
    # admin 用户无限量使用
    if not user.is_admin:
        if current > max :
            return msg
    #计算用户量
    count_usage(db,user_id)

    # 存入用户问题或者数据
    create_user_msgs(db=db, msg=msg, user_id=user_id)

    # 等待自动化回答
    user_question = msg.content.split("_")[-1]
    sys_prompt = get_prompt_by_category(db=db, category=msg.category).prompt
    
    res = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        temperature=0,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_question}
        ])
    ai_res = res.choices[0].message.content

    print(ai_res)

    data = json.loads(ai_res)
    ai_code = data["code"]
    ai_explain = data["explain"]

    ai_msg = {
        "time": "2025",
        "category":"auto",
        "code":ai_code,
        "content":"AI_"+ai_explain,
    }

    return ai_msg


# 获取所有的信息
@router.get("/", response_model=list[Msg])
def read_all_msgs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    msgs = get_msgs(db, skip=skip, limit=limit)
    return msgs


# chatgpt streaming
def get_openai_generator(question:str):
    completion = client.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant, skilled in explaining"},
            {"role": "user", "content": question},
            ],
        temperature=0,
        stream=True,
    )

    for chunk in completion:
        if "content" in chunk["choices"][0].delta:
            current_response = chunk["choices"][0].delta.content
            yield "data: " + current_response + "\n\n"

@router.post('/stream/')
async def stream(question: str):
    # 从 msg 中提炼出 question
    try:
        return StreamingResponse(get_openai_generator(question),media_type='text/event-stream')
    except Exception as e:
        raise HTTPException(status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


data_test= []

async def event_stream(sys_prompt:str):

    # 获取系统提示词

    # 获取历史记录

    # 生成流媒体数据块
    test_data = ["你还好吗，","最近过得怎么样，","有没有想念我，","在想些什么呢? ",data_test[-1], sys_prompt, "END"]
    for i in test_data:
        yield f"data: {i}\n\n".encode('utf-8')
        await asyncio.sleep(0.1)


@router.get("/fake-stream/")
async def fake_stream(cate:str,db: Session = Depends(get_db)):
    sys_prompt = get_prompt_by_category(db=db, category=cate).prompt

    return StreamingResponse(event_stream(sys_prompt), media_type="text/event-stream")



@router.post("/{user_id}/chat/",response_model=None)
async def fake_req(
    user_id: int, msg: MsgCreate, db: Session = Depends(get_db)
):
    # 获取用户的存量
    user= get_user(db,user_id)
    max = user.max_usage
    current = user.current_usage

    # 为了保险起见在服务端设置一边，主要靠客户端的
    if not user.is_admin:
        if current > max :
            return msg
    #计算用户量
    count_usage(db,user_id)
    

    # 用户存入数据库
    create_user_msgs(db=db, msg=msg, user_id=user_id)

    # 等待chatgpt回答
    user_text = msg.content.split("_")[-1]

    # 用户文本暂时存入data
    data_test.append(user_text)
    return {'user':user_text}


# 给定一个空数组，当用户停止使用时开始计时
# 当时间超过给定限度后，重置数组为空
# 当时间没有超时，数组正常使用

# 当用户为管理员时，停止重置数组