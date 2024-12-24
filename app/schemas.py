from pydantic import BaseModel


class UserBase(BaseModel):
    name:str
    password:str

class MessageData(BaseModel):
    message:str
    
class TokensResponse(BaseModel):
    accessToken:str
    refreshToken:str
class TokensResponseSwagger(BaseModel):
    access_token:str
    refresh_token:str

class MessageRes(BaseModel):
    message:str
    youWritten:bool

class ChatsRes(BaseModel):
    name:str