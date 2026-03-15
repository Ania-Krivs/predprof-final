from os import getenv

from dotenv import load_dotenv

load_dotenv()

MONGO_DSN = getenv("MONGO_DSN")
ENVIRONMENT = getenv("ENVIRONMENT")
ALGORITHM = getenv("ALGORITHM")
SECRET_KEY = getenv("SECRET_KEY")
SECRET_KEY_USER = getenv("SECRET_KEY_USER")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
