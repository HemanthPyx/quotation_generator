from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Quotation(Base):
    __tablename__ = 'quotations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quotation_number = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    quotation_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    project_type = Column(String(255), nullable=True)
    project_description = Column(Text, nullable=True)
    subtotal = Column(Numeric(12, 2), default=0)
    discount_total = Column(Numeric(12, 2), default=0)
    grand_total = Column(Numeric(12, 2), default=0)
    delivery_time = Column(Text, nullable=True)
    payment_terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    template_name = Column(String(50), default='professional')
    status = Column(String(20), default='Draft')
    pdf_path = Column(String(500), nullable=True)
    png_path = Column(String(500), nullable=True)
    jpeg_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    customer = relationship('Customer', back_populates='quotations')
    items = relationship('QuotationItem', back_populates='quotation', cascade='all, delete-orphan', order_by='QuotationItem.sort_order')

class QuotationItem(Base):
    __tablename__ = 'quotation_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quotation_id = Column(Integer, ForeignKey('quotations.id', ondelete='CASCADE'), nullable=False)
    service_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    amount = Column(Numeric(12, 2), default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    quotation = relationship('Quotation', back_populates='items')
