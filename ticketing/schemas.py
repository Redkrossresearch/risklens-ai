from pydantic import BaseModel
from typing import Optional
from datetime import date

class CreateTicketRequest(BaseModel):
    vulnerability_id: str
    assigned_to: str
    priority: str
    due_date: str


class UpdateTicketRequest(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


class TicketResponse(BaseModel):
    ticket_id: str
    vulnerability_id: str
    status: str
    assigned_to: str
    priority: str
    due_date: date