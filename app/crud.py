from sqlalchemy.orm import Session
from app.models import ConsultancyRequest
from app.schemas import ConsultancyRequestCreate, ConsultancyRequestApproval
from app.google_calendar import get_google_calendar_service

def create_consultancy_request(db: Session, request: ConsultancyRequestCreate):
    db_request = ConsultancyRequest(
        user_id=request.user_id,
        date=request.date,
        description=request.description,
        status="pending"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Create Google Calendar event here
    service = get_google_calendar_service()
    if service:
        # Logic for creating Google Calendar event
        pass

    return db_request

def get_consultancy_requests(db: Session):
    return db.query(ConsultancyRequest).all()

def update_consultancy_request_status(db: Session, request_id: int, status: str):
    db_request = db.query(ConsultancyRequest).filter(ConsultancyRequest.id == request_id).first()
    if db_request:
        db_request.status = status
        db.commit()
        return db_request
    return None
