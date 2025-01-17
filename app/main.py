from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.consultancy import router as consultancy_router
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Include API router for consultancy endpoints
app.include_router(consultancy_router, prefix="/consultancy", tags=["Consultancy"])

# Initialize Jinja2Templates to render HTML files
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/check_status", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("check_status.html", {"request": request})