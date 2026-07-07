from pydantic import BaseModel
from typing import Optional

class ComplianceModel(BaseModel):
    iso27001: str
    nist: str
    cis: str


class TicketModel(BaseModel):
    ticket_id: str
    status: str
    assigned_to: str
    due_date: str
    priority: str


class VulnerabilityModel(BaseModel):
    vulnerability_id: str
    title: str
    cve: str
    severity: str
    host: str
    description: str

    risk_title: Optional[str] = None
    business_impact: Optional[str] = None
    likelihood: Optional[str] = None
    risk_rating: Optional[str] = None
    risk_score: Optional[int] = None
    remediation: Optional[str] = None

    compliance: Optional[ComplianceModel] = None
    ticket: Optional[TicketModel] = None