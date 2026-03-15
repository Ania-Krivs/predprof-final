from app.utils.security import context_pass
from app.data.models import User
from app.data import schemas
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from app.utils.error import Error

import jwt

context_pass = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(request: schemas.UserSchema):
    user_exists = await User.find_one(User.email == request.email)
    if user_exists:
        raise Error.LOGIN_EXISTS
    hashed_password = context_pass.hash(request.password)[:72]
    user = User(
        username=request.username,
        hashed_password=hashed_password,
        email=request.email,
        role=request.role
    )
    
    await user.create()
    return user
    
async def authenticate_user(data: dict, expires_delta):
    access_token = await create_token(data, expires_delta)
    
    return access_token


async def create_token(data: dict, expires_delta: timedelta = None):
    '''
        data: login
    '''
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt


    
