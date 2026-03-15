from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    username: str
    role: str = "user"
    

class UserLogIn(BaseModel):
    user_token: str
    

class Token(BaseModel):
    access_token: str
    token_type: str


