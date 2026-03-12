from fastapi import APIRouter

from app.routes import analysis, health, image, property

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(property.router)
api_router.include_router(image.router)
api_router.include_router(analysis.router)

