from datetime import datetime
import enum
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Status Enum
class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MEETING_DONE = "meeting_done"

class ConsultancyRequest(Base):
    __tablename__ = "consultancy_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date = Column(DateTime)
    status = Column(String, default=RequestStatus.PENDING)
    description = Column(String)
    calendar_event_id = Column(String, nullable=True)
    
    
# class Asset(Base):
#     __tablename__ = "assets"

#     id = Column(Integer, primary_key=True, index=True)
#     request_id = Column(Integer, ForeignKey("consultancy_requests.id"))
#     title = Column(String)
#     description = Column(String)
#     image_path = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

# # schemas.py
# class AssetBase(BaseModel):
#     title: str
#     description: str
#     image_path: Optional[str] = None

# class AssetCreate(AssetBase):
#     pass

# class Asset(AssetBase):
#     id: int
#     request_id: int
#     created_at: datetime

#     class Config:
#         orm_mode = True
