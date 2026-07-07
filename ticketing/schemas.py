from pydantic import BaseModel, ConfigDict
from typing import Optional


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
    due_date: str

    model_config = ConfigDict(from_attributes=True)