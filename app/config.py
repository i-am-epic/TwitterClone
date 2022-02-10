from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str ="localhost"
    database_port:str="5432"
    database_password:str
    database_name:str
    database_username:str
    secret_key:str
    algorithm:str
    access_token_expiry_min:int=30
    
    class Config:
        env_file=".env"

settings = Settings()
