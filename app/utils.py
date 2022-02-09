from passlib.context import CryptContext
pwd_contex = CryptContext(schemes=["bcrypt"],deprecated = "auto")

def hash(password:str):
    return pwd_contex.hash(password)


def verify(plain_pswd,hashed_pswd):
    return pwd_contex.verify(plain_pswd,hashed_pswd)
