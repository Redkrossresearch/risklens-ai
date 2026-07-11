from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(String, primary_key=True, index=True)
    vulnerability_id = Column(String, nullable=False)
    assigned_to = Column(String, nullable=False)
    status = Column(String, default="Open")
    priority = Column(String, nullable=False)
    due_date = Column(String, nullable=False)