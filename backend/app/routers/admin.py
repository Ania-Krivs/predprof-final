from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
import secrets
from datetime import datetime

from app.data.models import User
from app.data import schemas
from app.utils.auth import hash_password
from app.utils.security import get_current_user
from app.utils.error import Error


router = APIRouter(prefix="/admin", tags=["Admin"])


async def verify_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Проверяет, что текущий пользователь является администратором
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуются права администратора"
        )
    return current_user


@router.post(
    "/users/create",
    response_model=schemas.AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового пользователя",
    description="Только администратор может создавать новых пользователей. Минимум требуется ввести Имя и Фамилию."
)
async def create_user_admin(
    request: schemas.AdminCreateUserRequest,
    admin: Annotated[User, Depends(verify_admin)]
) -> dict:
    """
    Создаёт нового пользователя в системе.
    
    **Параметры:**
    - **first_name** (required): Имя пользователя
    - **last_name** (required): Фамилия пользователя
    - **email** (required): Email пользователя (уникальный)
    - **username** (required): Username для входа (уникальный)
    - **password** (optional): Пароль. Если не указан, будет сгенерирован автоматически
    - **role** (optional): Роль пользователя. По умолчанию "user"
    
    **Возвращает:**
    - Информацию о созданном пользователе с ID
    """
    
    # Проверка уникальности email
    existing_email = await User.find_one(User.email == request.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован в системе"
        )
    
    # Проверка уникальности username
    existing_username = await User.find_one(User.username == request.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username уже занят"
        )
    
    # Генерация пароля если не указан
    password = request.password or secrets.token_urlsafe(12)
    hashed_password = hash_password(password)
    
    # Создание нового пользователя
    new_user = User(
        email=request.email,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=hashed_password,
        role=request.role,
        disabled=False
    )
    
    await new_user.insert()
    
    return {
        "id": str(new_user.id),
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "username": new_user.username,
        "role": new_user.role,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get(
    "/users/list",
    response_model=list[schemas.AdminUserResponse],
    summary="Список всех пользователей",
    description="Получить список всех пользователей в системе (только для администратора)"
)
async def list_users(
    admin: Annotated[User, Depends(verify_admin)]
) -> list[dict]:
    """
    Возвращает список всех пользователей в системе.
    """
    users = await User.find_all().to_list()
    
    return [
        {
            "id": str(user.id),
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "created_at": None
        }
        for user in users
    ]


@router.get(
    "/users/{user_id}",
    response_model=schemas.AdminUserResponse,
    summary="Получить информацию о пользователе",
    description="Получить подробную информацию о конкретном пользователе"
)
async def get_user_info(
    user_id: str,
    admin: Annotated[User, Depends(verify_admin)]
) -> dict:
    """
    Возвращает информацию о пользователе по ID.
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return {
        "id": str(user.id),
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": None
    }


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="Удалить пользователя из системы (только администратор)"
)
async def delete_user(
    user_id: str,
    admin: Annotated[User, Depends(verify_admin)]
) -> None:
    """
    Удаляет пользователя из системы по ID.
    """
    from bson import ObjectId
    
    try:
        user = await User.get(ObjectId(user_id))
        await user.delete()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
