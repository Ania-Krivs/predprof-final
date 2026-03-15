from beanie import Document, Link
from pydantic import EmailStr, BaseModel, Field
from typing import Optional
    
class SecretAdmin(Document):
    hashed_password: str


class AdminFront(Document):
    username: str = Field(json_schema_extra={"unique": True})
    disabled: bool = Field(default=False)
    full_name: str = Field(default=None)
    secret: Link[SecretAdmin] = Field()


class User(Document):
    email: EmailStr = Field(json_schema_extra={"unique": True})
    hashed_password: str
    first_name: str
    last_name: str
    role: str = Field(default="user")
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


