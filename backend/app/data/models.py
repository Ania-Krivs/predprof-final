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
    username: str
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    role: str = Field(default="user")
    disabled: bool = Field(default=False)
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


