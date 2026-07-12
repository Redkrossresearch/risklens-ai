from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from ticketing.repository import get_all_tickets

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/", response_class=HTMLResponse)
def dashboard(db: Session = Depends(get_db)):

    tickets = get_all_tickets(db)

    total = len(tickets)
    open_count = sum(1 for t in tickets if t.status == "Open")
    progress_count = sum(1 for t in tickets if t.status == "In Progress")
    closed_count = sum(1 for t in tickets if t.status == "Closed")
    high_count = sum(1 for t in tickets if t.priority == "High")

    percent = 0
    if total > 0:
        percent = int((closed_count / total) * 100)

    today = datetime.now().strftime("%d %B %Y")
    current_time = datetime.now().strftime("%d %B %Y %I:%M %p")
    table_rows = ""

    if total == 0:
        table_rows = """
        <tr>
            <td colspan="6">No Tickets Available</td>
        </tr>
        """

    if total > 0:
        for ticket in tickets:
            table_rows += f"""
            <tr>
                <td>{ticket.ticket_id}</td>
                <td>{ticket.vulnerability_id}</td>
                <td>{ticket.assigned_to}</td>
                <td>{ticket.status}</td>
                <td>{ticket.priority}</td>
                <td>{ticket.due_date}</td>
            </tr>
            """

        return f"""
<!DOCTYPE html>

<html>

<head>

<title>RiskLens AI Dashboard</title>

<style>

body{{
    font-family:Arial;
    background:#f4f6f9;
    margin:40px;
}}

h1{{
    color:#1f4e79;
}}

.cards{{
    display:flex;
    gap:20px;
    margin-top:30px;
}}

.card{{
    flex:1;
    padding:20px;
    border-radius:10px;
    color:white;
    text-align:center;
}}

.blue{{background:#007bff;}}
.red{{background:#dc3545;}}
.orange{{background:#fd7e14;}}
.green{{background:#28a745;}}

.progress-container{{
    width:100%;
    background:#ddd;
    border-radius:20px;
    margin-top:20px;
}}

.progress-bar{{
    width:{percent}%;
    background:#28a745;
    color:white;
    text-align:center;
    padding:10px;
    border-radius:20px;
}}

table{{
    width:100%;
    border-collapse:collapse;
    margin-top:40px;
    background:white;
}}

th,td{{
    border:1px solid #ccc;
    padding:10px;
    text-align:center;
}}

th{{
    background:#1f4e79;
    color:white;
}}

tr:nth-child(even){{
    background:#f2f2f2;
}}

.btn{{
    display:inline-block;
    margin-top:30px;
    padding:12px 20px;
    background:#1f4e79;
    color:white;
    text-decoration:none;
    border-radius:8px;
}}

</style>

</head>

<body>

<h1>🛡 RiskLens AI Dashboard</h1>
<h3>Welcome to RiskLens AI</h3>

<p>
Monitor vulnerabilities, track remediation progress, and manage security tickets from one dashboard.
</p>

<p><b>Last Updated:</b> {current_time}</p>

<div class="cards">

<div class="card blue">
<h2>{total}</h2>
<p>Total Tickets</p>
</div>

<div class="card red">
<h2>{open_count}</h2>
<p>Open</p>
</div>

<div class="card orange">
<h2>{progress_count}</h2>
<p>In Progress</p>
</div>

<div class="card green">
<h2>{closed_count}</h2>
<p>Closed</p>
</div>

<div class="card red">
    <h2>{high_count}</h2>
    <p>High Priority</p>
</div>

</div>

<h2>Overall Progress</h2>

<div class="progress-container">
<div class="progress-bar">
{percent}%
</div>
</div>

<a class="btn" href="/report/pdf">
📄 Download Risk Report PDF
</a>

<h2>Ticket Details</h2>

<table>

<tr>
<th>Ticket ID</th>
<th>Vulnerability ID</th>
<th>Assigned To</th>
<th>Status</th>
<th>Priority</th>
<th>Due Date</th>
</tr>

{table_rows}

</table>

</body>

</html>
"""