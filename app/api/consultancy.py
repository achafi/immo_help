import os
import shutil
from typing import List
from fastapi import APIRouter, File, HTTPException, Depends, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.utils import send_admin_notification
from app.db import get_db
from pathlib import Path
from app.google_calendar import get_google_calendar_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")  # Adjust the directory as needed
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
    
    if id is None:
        # Show the initial status check form if no ID is provided
        return templates.TemplateResponse("check_status.html", {
            "request": request
        })

    # Fetch the request status using the existing route logic
    db_request = db.query(models.ConsultancyRequest).filter(models.ConsultancyRequest.id == id).first()

    if not db_request:
        return HTMLResponse(content="Request not found.", status_code=404)

    # If status is assets_added, redirect to assets view
    if db_request.status == models.RequestStatus.ASSETS_ADDED:
        return templates.TemplateResponse("assets_view.html", {
            "request": request,
            "assets": db.query(models.Asset).filter(models.Asset.request_id == id).all(),
            "consultancy_request": db_request,
        })
    
    # For other statuses, show the regular status page
    return templates.TemplateResponse("status.html", {
        "request": request,
        "id": id,  # Make sure to include the ID
        "status": db_request.status,
        "date": db_request.date,
        "description": db_request.description,
    })
    
# Add a new endpoint to view assets directly
@router.get("/view-assets/{request_id}", response_class=HTMLResponse)
async def view_assets(request: Request, request_id: int, db: Session = Depends(get_db)):
    db_request = db.query(models.ConsultancyRequest).filter(
        models.ConsultancyRequest.id == request_id
    ).first()
    
    if not db_request:
        return HTMLResponse(content="Request not found.", status_code=404)
    
    if db_request.status != models.RequestStatus.ASSETS_ADDED:
        return HTMLResponse(content="No assets available for this request.", status_code=400)
    
    assets = db.query(models.Asset).filter(models.Asset.request_id == request_id).all()
    
    return templates.TemplateResponse("assets_view.html", {
        "request": request,
        "assets": assets,
        "consultancy_request": db_request
    })
    
    
@router.get("/add-assets/{request_id}", response_class=HTMLResponse)
async def add_assets_page(request: Request, request_id: int, db: Session = Depends(get_db)):
    # Fetch the request based on the ID
    db_request = db.query(models.ConsultancyRequest).filter(
        models.ConsultancyRequest.id == request_id
    ).first()
    if not db_request:
        return HTMLResponse(content="Request not found.", status_code=404)
    return templates.TemplateResponse("add_assets.html", {
        "request": request,
        "request_id": request_id,
        "request_status": db_request.status
    })

@router.post("/add_assets/{request_id}", response_model=List[schemas.Asset])
async def add_assets(
    request_id: int,
    assets_list: schemas.AssetsList,
    db: Session = Depends(get_db)
):
    try:
        # Print the received data for debugging
        print(f"Received request_id: {request_id}")
        print(f"Received assets_list: {assets_list}")

        db_request = db.query(models.ConsultancyRequest).filter(
            models.ConsultancyRequest.id == request_id
        ).first()
        
        if not db_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if db_request.status not in [models.RequestStatus.MEETING_DONE , models.RequestStatus.ASSETS_ADDED]:
            raise HTTPException(
                status_code=400, 
                detail=f"Can only add assets to requests with 'meeting_done' status. Current status: {db_request.status}"
            )

        db_assets = []
        for asset in assets_list.assets:
            print(f"Processing asset: {asset}")
            db_asset = models.Asset(
                request_id=request_id,
                title=asset.title,
                description=asset.description,
                image_path=asset.image_path
            )
            db.add(db_asset)
            db_assets.append(db_asset)
        
        # Update request status
        db_request.status = models.RequestStatus.ASSETS_ADDED
        
        db.commit()
        for asset in db_assets:
            db.refresh(asset)
        
        return db_assets
    except Exception as e:
        print(f"Error in add_assets: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Add a new endpoint for file upload
@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))