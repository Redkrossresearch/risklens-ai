from sqlalchemy.orm import Session

from ticketing.models import Ticket
from ticketing.repository import (
    create_ticket as create_ticket_repo,
    get_ticket_by_id,
    update_ticket as update_ticket_repo,
    delete_ticket as delete_ticket_repo,
)
from ticketing.schemas import CreateTicketRequest, UpdateTicketRequest
from ticketing.utils import generate_ticket_id


def create_ticket(db: Session, ticket_data: CreateTicketRequest):
    """
    Create a new remediation ticket.
    """

    ticket = Ticket(
        ticket_id=generate_ticket_id(),
        vulnerability_id=ticket_data.vulnerability_id,
        assigned_to=ticket_data.assigned_to,
        status="Open",
        priority=ticket_data.priority,
        due_date=ticket_data.due_date,
    )

    return create_ticket_repo(db, ticket)


def update_ticket(
    db: Session,
    ticket_id: str,
    ticket_data: UpdateTicketRequest,
):
    """
    Update an existing ticket.
    """

    ticket = get_ticket_by_id(db, ticket_id)

    if ticket is None:
        return None

    if ticket_data.status is not None:
        ticket.status = ticket_data.status

    if ticket_data.assigned_to is not None:
        ticket.assigned_to = ticket_data.assigned_to

    if ticket_data.priority is not None:
        ticket.priority = ticket_data.priority

    if ticket_data.due_date is not None:
        ticket.due_date = ticket_data.due_date

    return update_ticket_repo(db, ticket)


def delete_ticket(db: Session, ticket_id: str):
    """
    Delete a ticket.
    """

    ticket = get_ticket_by_id(db, ticket_id)

    if ticket is None:
        return False

    delete_ticket_repo(db, ticket)
    return True