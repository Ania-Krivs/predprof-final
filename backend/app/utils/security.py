from typing import Annotated

from app import ALGORITHM, SECRET_KEY
from app.data.models import User, TokenData
from app.utils.error import Error
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from jwt.exceptions import InvalidTokenError
import jwt

context_pass = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

def verify_password(plain_password, hashed_password):

    return context_pass.verify(plain_password, hashed_password)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(str(token), str(SECRET_KEY), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise Error.UNAUTHORIZED_INVALID
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise Error.UNAUTHORIZED_INVALID
    
    user = await User.find_one(User.login == token_data.username, fetch_links=True)
    if user is None:
        raise Error.UNAUTHORIZED_INVALID
    
    return user