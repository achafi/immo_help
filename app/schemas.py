from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .models import RequestStatus

class ConsultancyRequestCreate(BaseModel):
    user_id: int
    date: datetime
    description: str

class ConsultancyRequestResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    status: str
    description: str

class ConsultancyRequestApproval(BaseModel):
    request_id: int
    status: RequestStatus

class AssetBase(BaseModel):
    """Base schema with common attributes for assets"""
    title: str
    description: str
    image_path: Optional[str] = None

class AssetCreate(AssetBase):
    """Schema for creating a new asset"""
    pass

class Asset(AssetBase):
    """Schema for asset responses, includes database fields"""
    id: int
    request_id: int
    created_at: datetime

    class Config:
        """Enables ORM mode for Pydantic"""
        orm_mode = True

# Optional: If you want to update assets later
class AssetUpdate(BaseModel):
    """Schema for updating an existing asset"""
    title: Optional[str] = None
    description: Optional[str] = None
    image_path: Optional[str] = None
    
    
# class ConsultancyRequestResponse(BaseModel):
#     id: int
#     user_id: int
#     date: datetime
#     status: str
#     description: str
#     assets: List[Asset]  # Include a list of assets

#     class Config:
#         orm_mode = True