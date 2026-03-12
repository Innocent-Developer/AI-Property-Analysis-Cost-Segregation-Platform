import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.property import PropertyCreate, PropertyResponse
from app.services.property_service import create_property, get_property, list_properties


router = APIRouter(tags=["properties"])


@router.post("/property", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property_endpoint(
    payload: PropertyCreate,
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    property_obj = await create_property(db, payload)
    return PropertyResponse.model_validate(property_obj)


@router.get("/property/{property_id}", response_model=PropertyResponse)
async def get_property_endpoint(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    property_obj = await get_property(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return PropertyResponse.model_validate(property_obj)


@router.get("/properties", response_model=list[PropertyResponse])
async def list_properties_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[PropertyResponse]:
    properties = await list_properties(db, skip=skip, limit=limit)
    return [PropertyResponse.model_validate(p) for p in properties]

