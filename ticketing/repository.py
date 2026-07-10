from sqlalchemy.orm import Session
from ticketing.models import Ticket

def create_ticket(db: Session, ticket: Ticket):
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_ticket_by_id(db: Session, ticket_id: str):
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

def get_all_tickets(db: Session):
    return db.query(Ticket).all()

def update_ticket(db: Session, ticket: Ticket):
    db.commit()
    db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, ticket: Ticket):
    db.delete(ticket)
    db.commit()