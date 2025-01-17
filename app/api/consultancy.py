from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.utils import send_admin_notification
from app.db import get_db
from app.google_calendar import get_google_calendar_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")  # Adjust the directory as needed


@router.post("/request_consultancy", response_model=schemas.ConsultancyRequestResponse)
async def create_consultancy_request(request: schemas.ConsultancyRequestCreate, db: Session = Depends(get_db)):
    db_request = crud.create_consultancy_request(db=db, request=request)
    #await send_admin_notification(db_request)
    return db_request

@router.get("/get_consultancy_requests", response_model=List[schemas.ConsultancyRequestResponse])
def get_consultancy_requests(db: Session = Depends(get_db)):
    return crud.get_consultancy_requests(db=db)

@router.post("/approve_consultancy", response_model=schemas.ConsultancyRequestResponse)
async def approve_consultancy_request(approval: schemas.ConsultancyRequestApproval, db: Session = Depends(get_db)):
    db_request = crud.update_consultancy_request_status(db, approval.request_id, approval.status)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Handle calendar event deletion if rejected
    if approval.status == "rejected" and db_request.calendar_event_id:
        service = get_google_calendar_service()
        if service:
            service.events().delete(
                calendarId='primary',
                eventId=db_request.calendar_event_id
            ).execute()
    return db_request

@router.get("/check_request_status/{request_id}", response_model=schemas.ConsultancyRequestResponse)
def check_request_status(request_id: int, db: Session = Depends(get_db)):
    db_request = db.query(models.ConsultancyRequest).filter(models.ConsultancyRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    return db_request


@router.get("/check-status", response_class=HTMLResponse)
async def check_status_page(request: Request, id: int, db: Session = Depends(get_db)):
    # Fetch the request status using the existing route logic
    db_request = db.query(models.ConsultancyRequest).filter(models.ConsultancyRequest.id == id).first()

    if not db_request:
        return HTMLResponse(content="Request not found.", status_code=404)

    # Render the page with the fetched data
    return templates.TemplateResponse("status.html", {
        "request": request,
        "status": db_request.status,
        "date": db_request.date,
        "description": db_request.description,
    })