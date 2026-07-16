from sqlalchemy import Column, String, Integer, Text, JSON
from database import Base

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="viewer")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    vulnerability_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    cve = Column(String)
    severity = Column(String)
    host = Column(String)
    description = Column(Text)
    risk_title = Column(String, nullable=True)
    executive_summary = Column(Text, nullable=True)
    business_impact = Column(Text, nullable=True)
    likelihood = Column(String, nullable=True)
    risk_rating = Column(String, nullable=True)
    risk_score = Column(Integer, nullable=True)
    remediation = Column(Text, nullable=True)
    compliance = Column(JSON, nullable=True)
    ticket = Column(JSON, nullable=True)