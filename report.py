from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

from database import get_db
from ticketing.repository import get_all_tickets

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


@router.get("/pdf")
def generate_pdf(db: Session = Depends(get_db)):

    tickets = get_all_tickets(db)

    pdf_path = os.path.join(REPORT_DIR, "Risk_Report.pdf")

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>RiskLens AI - Risk Closure Report</b>", styles["Title"])
    )

    elements.append(
        Paragraph(f"Total Tickets : {len(tickets)}", styles["Heading2"])
    )

    data = [
        [
            "Ticket ID",
            "Vulnerability",
            "Assigned To",
            "Status",
            "Priority",
            "Due Date"
        ]
    ]

    for ticket in tickets:
        data.append([
            ticket.ticket_id,
            ticket.vulnerability_id,
            ticket.assigned_to,
            ticket.status,
            ticket.priority,
            str(ticket.due_date)
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))

    elements.append(table)

    doc.build(elements)

    return FileResponse(
        pdf_path,
        filename="Risk_Report.pdf",
        media_type="application/pdf"
    )