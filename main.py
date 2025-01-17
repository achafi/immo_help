# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import enum
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
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

# Database Model
class ConsultancyRequest(Base):
    __tablename__ = "consultancy_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    date = Column(DateTime)
    status = Column(String, default=RequestStatus.PENDING)
    description = Column(String)
    calendar_event_id = Column(String, nullable=True)

# Pydantic Models
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

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error setting up Google Calendar service: {e}")
        return None

# Endpoints
@app.post("/request_consultancy", response_model=ConsultancyRequestResponse)
async def create_consultancy_request(
    request: ConsultancyRequestCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create database entry
        db_request = ConsultancyRequest(
            user_id=request.user_id,
            date=request.date,
            description=request.description,
            status=RequestStatus.PENDING
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        # Try to create Google Calendar event
        service = get_google_calendar_service()
        if service:
            try:
                event = {
                    'summary': f'Consultancy Request - User {request.user_id}',
                    'description': request.description,
                    'start': {
                        'dateTime': request.date.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': (request.date.replace(hour=request.date.hour + 1)).isoformat(),
                        'timeZone': 'UTC',
                    },
                }
                calendar_event = service.events().insert(calendarId='primary', body=event).execute()
                db_request.calendar_event_id = calendar_event['id']
                db.commit()
            except Exception as e:
                print(f"Error creating calendar event: {e}")

        return ConsultancyRequestResponse(
            id=db_request.id,
            user_id=db_request.user_id,
            date=db_request.date,
            status=db_request.status,
            description=db_request.description
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_consultancy_requests", response_model=List[ConsultancyRequestResponse])
def get_consultancy_requests(db: Session = Depends(get_db)):
    requests = db.query(ConsultancyRequest).all()
    return requests

@app.post("/approve_consultancy")
async def approve_consultancy_request(
    approval: ConsultancyRequestApproval,
    db: Session = Depends(get_db)
):
    request = db.query(ConsultancyRequest).filter(ConsultancyRequest.id == approval.request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request.status = approval.status
    db.commit()

    # Update Google Calendar event if rejected
    if approval.status == RequestStatus.REJECTED and request.calendar_event_id:
        service = get_google_calendar_service()
        if service:
            try:
                service.events().delete(
                    calendarId='primary',
                    eventId=request.calendar_event_id
                ).execute()
            except Exception as e:
                print(f"Error deleting calendar event: {e}")

    return {"message": f"Request {approval.status}"}

@app.get("/check_request_status/{request_id}", response_model=ConsultancyRequestResponse)
def check_request_status(request_id: int, db: Session = Depends(get_db)):
    request = db.query(ConsultancyRequest).filter(ConsultancyRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
# Create tables
Base.metadata.create_all(bind=engine)