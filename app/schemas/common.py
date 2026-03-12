from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

