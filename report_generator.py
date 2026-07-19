from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import date
from typing import List, Dict
import json
import os

def get_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('Title', fontSize=24, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a1a'), alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle('Subtitle', fontSize=11, fontName='Helvetica',
            textColor=colors.HexColor('#555555'), alignment=TA_CENTER, spaceAfter=2),
        "section": ParagraphStyle('Section', fontSize=13, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#c0392b'), spaceBefore=14, spaceAfter=6),
        "subsection": ParagraphStyle('Subsection', fontSize=11, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2c3e50'), spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle('Body', fontSize=10, fontName='Helvetica',
            textColor=colors.HexColor('#333333'), spaceAfter=4, leading=15),
        "bullet_done": ParagraphStyle('BulletDone', fontSize=10, fontName='Helvetica',
            textColor=colors.HexColor('#1baf7a'), spaceAfter=3, leftIndent=16, leading=14),
        "bullet_warn": ParagraphStyle('BulletWarn', fontSize=10, fontName='Helvetica',
            textColor=colors.HexColor('#e24b4a'), spaceAfter=3, leftIndent=16, leading=14),
        "small": ParagraphStyle('Small', fontSize=9, fontName='Helvetica',
            textColor=colors.HexColor('#777777'), alignment=TA_CENTER),
    }

def generate_executive_report(vulnerabilities: list, compliance: dict, output_path: str = "reports/executive_report.pdf"):
    os.makedirs("reports", exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    
    s = get_styles()
    story = []

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("RiskLens AI", s["title"]))
    story.append(Paragraph("Executive Risk Report", s["subtitle"]))
    story.append(Paragraph(f"Date: {date.today().strftime('%B %d, %Y')}  |  Red Cross Research Foundation", s["small"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#c0392b')))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("1. Executive Summary", s["section"]))
    total = len(vulnerabilities)
    critical = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "critical")
    high = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "high")
    medium = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "medium")
    low = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "low")
    
    story.append(Paragraph(
        f"This report presents a high-level overview of the organization's current cybersecurity posture. "
        f"A total of <b>{total}</b> vulnerabilities were identified, of which <b>{critical}</b> are critical and "
        f"<b>{high}</b> are high severity, requiring immediate attention.", s["body"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("2. Risk Overview", s["section"]))
    risk_data = [
        ["Severity", "Count", "Action Required"],
        ["Critical", str(critical), "Immediate - within 24 hours"],
        ["High",     str(high),     "Urgent - within 7 days"],
        ["Medium",   str(medium),   "Planned - within 30 days"],
        ["Low",      str(low),      "Monitor - within 90 days"],
        ["Total",    str(total),    "-"],
    ]
    risk_table = Table(risk_data, colWidths=[4*cm, 3*cm, 9*cm])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('TEXTCOLOR', (0,1), (0,1), colors.HexColor('#e24b4a')),
        ('TEXTCOLOR', (0,2), (0,2), colors.HexColor('#eda100')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(risk_table)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("3. Compliance Score", s["section"]))
    comp_data = [["Framework", "Score", "Status"]]
    for framework, score in compliance.items():
        status = "Pass" if score >= 75 else "Needs Improvement" if score >= 55 else "Fail"
        comp_data.append([framework, f"{score}%", status])
    
    comp_table = Table(comp_data, colWidths=[5*cm, 3*cm, 8*cm])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(comp_table)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("4. Top 5 Risks - Business Impact", s["section"]))
    top5 = sorted(vulnerabilities, key=lambda x: x.get("severity","").lower() == "critical", reverse=True)[:5]
    for i, v in enumerate(top5, 1):
        story.append(Paragraph(f"<b>{i}. {v.get('title', 'Unknown')}</b>", s["subsection"]))
        story.append(Paragraph(f"Severity: {v.get('severity','N/A')}  |  Host: {v.get('host','N/A')}  |  CVE: {v.get('cve','N/A')}", s["body"]))
        if v.get("business_impact"):
            story.append(Paragraph(f"Business Impact: {v.get('business_impact')}", s["body"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("5. Recommendations", s["section"]))
    recommendations = [
        "Immediately patch all Critical vulnerabilities identified in this report.",
        "Enforce strong password policies across all systems.",
        "Review and update SSL certificates before expiry.",
        "Conduct regular vulnerability scans - minimum monthly.",
        "Achieve GDPR and PCI-DSS compliance - currently below threshold.",
    ]
    for rec in recommendations:
        story.append(Paragraph(f"-  {rec}", s["bullet_done"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Paragraph("RiskLens AI  |  Executive Report  |  Red Cross Research Foundation  |  Confidential", s["small"]))

    doc.build(story)
    return output_path


def generate_technical_report(vulnerabilities: list, compliance: dict, output_path: str = "reports/technical_report.pdf"):
    os.makedirs("reports", exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    
    s = get_styles()
    story = []

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("RiskLens AI", s["title"]))
    story.append(Paragraph("Technical Vulnerability Report", s["subtitle"]))
    story.append(Paragraph(f"Date: {date.today().strftime('%B %d, %Y')}  |  Red Cross Research Foundation", s["small"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2c3e50')))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("1. Technical Summary", s["section"]))
    total = len(vulnerabilities)
    critical = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "critical")
    high = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "high")
    medium = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "medium")
    low = sum(1 for v in vulnerabilities if v.get("severity","").lower() == "low")

    story.append(Paragraph(
        f"Total vulnerabilities scanned: <b>{total}</b>. "
        f"Breakdown - Critical: <b>{critical}</b>, High: <b>{high}</b>, "
        f"Medium: <b>{medium}</b>, Low: <b>{low}</b>.", s["body"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("2. Full Vulnerability List", s["section"]))
    
    vuln_data = [["#", "Title", "CVE", "Severity", "Host"]]
    for i, v in enumerate(vulnerabilities, 1):
        vuln_data.append([
            str(i),
            v.get("title", "Unknown")[:35],
            v.get("cve", "N/A"),
            v.get("severity", "N/A"),
            v.get("host", "N/A")[:20],
        ])
    
    vuln_table = Table(vuln_data, colWidths=[1*cm, 6*cm, 3*cm, 2.5*cm, 3.5*cm])
    vuln_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(vuln_table)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("3. Compliance Details", s["section"]))
    comp_data = [["Framework", "Score", "Controls", "Status", "Action"]]
    controls = {"ISO 27001": "18", "NIST CSF": "23", "GDPR": "11", "PCI-DSS": "12", "CIS v8": "18", "HIPAA": "9"}
    for framework, score in compliance.items():
        status = "Pass" if score >= 75 else "Review" if score >= 55 else "Fail"
        action = "Maintain" if score >= 75 else "Improve" if score >= 55 else "Immediate Action"
        comp_data.append([framework, f"{score}%", controls.get(framework, "N/A"), status, action])
    
    comp_table = Table(comp_data, colWidths=[3.5*cm, 2*cm, 2.5*cm, 2.5*cm, 5*cm])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(comp_table)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("4. Remediation Steps", s["section"]))
    for i, v in enumerate(vulnerabilities[:10], 1):
        story.append(Paragraph(f"<b>{i}. {v.get('title','Unknown')}</b>  -  {v.get('severity','N/A')}", s["subsection"]))
        if v.get("remediation"):
            story.append(Paragraph(f"Fix: {v.get('remediation')}", s["body"]))
        else:
            story.append(Paragraph(f"CVE: {v.get('cve','N/A')}  |  Host: {v.get('host','N/A')}  |  Apply latest security patches.", s["body"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Paragraph("RiskLens AI  |  Technical Report  |  Red Cross Research Foundation  |  Confidential", s["small"]))

    doc.build(story)
    return output_path