from app.models import ConsultancyRequest
from app.db import get_db
from app.schemas import ConsultancyRequestCreate, ConsultancyRequestApproval
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.google_calendar import get_google_calendar_service

def create_consultancy_request(request: ConsultancyRequestCreate, db: Session):
    try:
        # Create database entry
        db_request = ConsultancyRequest(
            user_id=request.user_id,
            date=request.date,
            description=request.description,
            status="pending"
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        # Create Google Calendar event
        service = get_google_calendar_service()
        if service:
            event = {
                'summary': f'Consultancy Request - User {request.user_id}',
                'description': request.description,
                'start': {'dateTime': request.date.isoformat(), 'timeZone': 'UTC'},
                'end': {'dateTime': (request.date.replace(hour=request.date.hour + 1)).isoformat(), 'timeZone': 'UTC'}
            }
            calendar_event = service.events().insert(calendarId='primary', body=event).execute()
            db_request.calendar_event_id = calendar_event['id']
            db.commit()
        return db_request
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
