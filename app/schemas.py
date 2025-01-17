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
