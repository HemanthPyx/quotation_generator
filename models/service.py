from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, func
from database import Base

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    default_price = Column(Numeric(10, 2), default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
