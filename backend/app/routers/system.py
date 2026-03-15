from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])

@router.get('/ping')
async def ping() -> str:
    return 'pong'