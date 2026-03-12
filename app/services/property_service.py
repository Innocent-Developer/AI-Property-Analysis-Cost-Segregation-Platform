import uuid
from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property
from app.schemas.property import PropertyCreate


async def create_property(db: AsyncSession, data: PropertyCreate) -> Property:
    property_obj = Property(
        user_id=data.user_id,
        address=data.address,
        property_type=data.property_type,
        improvement_basis=data.improvement_basis,
    )

    db.add(property_obj)
    await db.commit()
    await db.refresh(property_obj)
    return property_obj


async def get_property(db: AsyncSession, property_id: uuid.UUID) -> Property | None:
    stmt: Select[tuple[Property]] = select(Property).where(Property.id == property_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_properties(db: AsyncSession, skip: int = 0, limit: int = 50) -> Sequence[Property]:
    stmt: Select[tuple[Property]] = (
        select(Property)
        .order_by(Property.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

