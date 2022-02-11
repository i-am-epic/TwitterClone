from operator import mod
from pyexpat import model
from fastapi import FastAPI,Response,status,HTTPException, Depends, APIRouter
from .. import schemas,database,models,utils,oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm=Depends(),db:Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid email or password")
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid email or password")
    print(user.id)

    access_token = oauth2.create_access_token(data = {"user_id":user.id,"admin":user.admin})
    print(access_token)
    return{"access_token":access_token,"token_type":"bearer","user_name":user_credentials.username}

