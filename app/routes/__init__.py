from fastapi import APIRouter

from app.routes import analysis, health, image, property, report

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(property.router)
api_router.include_router(image.router)
api_router.include_router(analysis.router)
api_router.include_router(report.router)

