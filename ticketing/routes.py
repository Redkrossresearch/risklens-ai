from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from ticketing.schemas import (
    CreateTicketRequest,
    UpdateTicketRequest,
    TicketResponse,
)
from ticketing.service import (
    create_ticket,
    update_ticket,
    delete_ticket,
)
from ticketing.repository import (
    get_all_tickets,
    get_ticket_by_id,
)

router = APIRouter(
    prefix="/tickets",
    tags=["Ticketing"]
)

@router.post("/", response_model=TicketResponse)
def create_new_ticket(ticket: CreateTicketRequest, db: Session = Depends(get_db)):
    return create_ticket(db, ticket)

@router.get("/", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return get_all_tickets(db)

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(ticket_id: str, ticket_data: UpdateTicketRequest, db: Session = Depends(get_db)):
    ticket = update_ticket(db, ticket_id, ticket_data)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.delete("/{ticket_id}")
def remove_ticket(ticket_id: str, db: Session = Depends(get_db)):
    success = delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket deleted successfully"}