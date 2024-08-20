from pydantic import BaseModel

class PromptBase(BaseModel):
    category:str | None = None
    prompt:str | None = None


class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id:int
    count:str | None = None
    
    class Config:
        from_attributes = True
