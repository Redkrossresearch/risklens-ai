from sqlalchemy.orm import Session

from ticketing.models import Ticket


def create_ticket(db: Session, ticket: Ticket):
    """
    Save a new ticket to the database.
    """
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket_by_id(db: Session, ticket_id: str):
    """
    Fetch a ticket using its ticket ID.
    """
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def get_all_tickets(db: Session):
    """
    Fetch all tickets.
    """
    return db.query(Ticket).all()


def update_ticket(db: Session, ticket: Ticket):
    """
    Save changes made to an existing ticket.
    """
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket: Ticket):
    """
    Delete a ticket from the database.
    """
    db.delete(ticket)
    db.commit()