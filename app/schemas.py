from pydantic import BaseModel


class UserBase(BaseModel):
    name:str
    password:str

class MessageData(BaseModel):
    message:str