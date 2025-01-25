from datetime import datetime
import enum
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.orm import relationship

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
    ASSETS_ADDED = "assets_added"

class ConsultancyRequest(Base):
    __tablename__ = "consultancy_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date = Column(DateTime)
    status = Column(String, default=RequestStatus.PENDING)
    description = Column(String)
    calendar_event_id = Column(String, nullable=True)
    
    
class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("consultancy_requests.id"))
    title = Column(String)
    description = Column(String)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AssetFeedback(Base):
    __tablename__ = "asset_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    feedback_type = Column(String)  # 'like' or 'dislike'
    created_at = Column(DateTime, default=datetime.utcnow)

class AssetSuggestion(Base):
    __tablename__ = "asset_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    suggestion_text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
Base.metadata.create_all(bind=engine)