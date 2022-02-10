from datetime import datetime
from pydantic import BaseModel,EmailStr
from typing import Optional

    
class NewUser(BaseModel):
    username:str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id:int
    username:str
    email:EmailStr

    class Config:
        orm_mode = True

#Schema of posts
class PostBase(BaseModel): 
    title:str
    content:Optional[str]= ""
    cat_name:str


class PostCreate(PostBase):
    published:Optional[bool]=True

class PostDel(PostBase):
    published:Optional[bool]=True


class Post(PostBase):
    published:Optional[bool]=True
    postid: int
    created_at: datetime
    owner_id: int
    
    class Config:
        orm_mode = True

'''class PostOut(PostBase):
    published:Optional[bool]=True
    postid: int
    created_at: datetime
    owner_id: int
    owner:UserOut
    class Config:
        orm_mode = True
'''

class NewCat(BaseModel):
    cat_name:str
    description: str

class Retweet(BaseModel):
    user_id:int
    post_id:int
    created_at: datetime


class CatOut(BaseModel):
    cat_id:int
    description: str
    owner_id:int   
    cat_name:str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]=None
