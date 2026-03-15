from contextlib import asynccontextmanager

from beanie import init_beanie, Document, UnionDoc
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app import MONGO_DSN, ENVIRONMENT, projectConfig
from app.routers import system, auth, ml_work, admin, civilization

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGO_DSN, uuidRepresentation='standard')
    await init_beanie(
        database=client.get_default_database(),
        document_models=Document.__subclasses__() + UnionDoc.__subclasses__()
    )
    yield
    
if ENVIRONMENT == "prod":
    app = FastAPI(
        title=projectConfig.__projname__,
        version=projectConfig.__version__,
        description=projectConfig.__description__,
        lifespan=lifespan,
        docs_url="/api/docs",
    )

else:
    app = FastAPI(
        title=projectConfig.__projname__,
        version=projectConfig.__version__,
        description=projectConfig.__description__,
        lifespan=lifespan
    )

api_router = APIRouter(prefix="/api")    

api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(ml_work.router)
api_router.include_router(admin.router)
api_router.include_router(civilization.router)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)