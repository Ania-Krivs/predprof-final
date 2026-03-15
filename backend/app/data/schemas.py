from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "user"
    age: Optional[int] = None
    gender: Optional[str] = None


class RequestTeacher(UserSchema):
    pass


class UserLogIn(BaseModel):
    user_token: str
    

class Token(BaseModel):
    access_token: str
    token_type: str
