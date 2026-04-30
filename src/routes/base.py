from fastapi import APIRouter, Depends
from src.helpers import get_settings, Settings

base_router = APIRouter()


@base_router.get("/")
async def root(settings: Settings = Depends(get_settings)):
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION
    }