from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base

class CompanySettings(Base):
    __tablename__ = 'company_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=True)
    logo_path = Column(String(500), nullable=True)
    tagline = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    gst_number = Column(String(50), nullable=True)
    default_payment_terms = Column(Text, nullable=True, default='50% advance before project commencement and 50% before final deployment.')
    default_delivery_terms = Column(Text, nullable=True, default='5-7 working days after receiving all required content.')
    default_validity_days = Column(Integer, default=15)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
