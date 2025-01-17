import enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime
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

class ConsultancyRequest(Base):
    __tablename__ = "consultancy_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date = Column(DateTime)
    status = Column(String, default=RequestStatus.PENDING)
    description = Column(String)
    calendar_event_id = Column(String, nullable=True)
