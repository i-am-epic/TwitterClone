from datetime import datetime
from pydantic import BaseModel,EmailStr, conint
from typing import Optional

    
class NewUser(BaseModel):
    username:str
    email: EmailStr
    password: str
    admin:Optional[bool]=False
    description: Optional[str]=False



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
    
    class Config:
        orm_mode = True

class PostOut(Post):
    postid: int
    created_at: datetime
    owner_id: int
    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id:int
    dir:conint(ge=0,le=1)



class NewCat(BaseModel):
    cat_name:str
    description: str

class Retweet(BaseModel):
    post_id:int
    dir:conint(ge=0,le=1)


class CatOut(BaseModel):
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
    user_name:str


class TokenData(BaseModel):
    id: Optional[str]=None
