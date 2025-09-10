from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CatalogItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    source: Optional[str] = None
    item_code: Optional[str] = None
    item_type: Optional[str] = None
    suggested_price: Optional[float] = None

class CatalogItemCreate(CatalogItemBase):
    pass

class CatalogItem(CatalogItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True