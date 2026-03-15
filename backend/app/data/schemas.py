from pydantic import BaseModel, EmailStr
from typing import Optional, Dict


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


class CivilizationClassificationResponse(BaseModel):
    civilization: str
    confidence: float
    class_id: int
    all_predictions: Dict[str, float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "civilization": "kepler-22b",
                "confidence": 0.9543,
                "class_id": 14,
                "all_predictions": {
                    "55_cancri_bc": 0.0012,
                    "gliese": 0.0098,
                    "kepler-22b": 0.9543
                }
            }
        }


class AdminCreateUserRequest(BaseModel):
    """Схема запроса на создание пользователя администратором"""
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: Optional[str] = None
    role: str = "user"
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "ivan@example.com",
                "username": "ivan_ivanov",
                "password": "secure_password_123",
                "role": "user"
            }
        }


class AdminUserResponse(BaseModel):
    """Схема ответа при создании пользователя"""
    id: str
    first_name: str
    last_name: str
    email: str
    username: str
    role: str
    created_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "first_name": "Иван",
                "last_name": "Иванов",
                "email": "ivan@example.com",
                "username": "ivan_ivanov",
                "role": "user",
                "created_at": "2026-03-15T12:00:00"
            }
        }


class AdminErrorResponse(BaseModel):
    """Схема ошибки при создании пользователя"""
    detail: str
    error_code: str


