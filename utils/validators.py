from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator

class CustomerInput(BaseModel):
    name: str = Field(min_length=1)
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class QuotationItemInput(BaseModel):
    service_name: str = Field(min_length=1)
    description: Optional[str] = None
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    discount: float = Field(ge=0)
    
    @model_validator(mode='after')
    def check_discount(self) -> 'QuotationItemInput':
        if self.discount > (self.quantity * self.unit_price):
            raise ValueError("Discount cannot exceed the total price (quantity * unit_price)")
        return self

class QuotationInput(BaseModel):
    customer: CustomerInput
    items: List[QuotationItemInput] = Field(min_length=1)
    project_type: Optional[str] = None
    project_description: Optional[str] = None
    delivery_time: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None

def validate_quotation_data(data: dict) -> tuple[bool, list[str]]:
    try:
        QuotationInput(**data)
        return True, []
    except ValueError as e:
        errors = []
        if hasattr(e, 'errors') and callable(e.errors):
            for error in e.errors():
                loc = " -> ".join([str(l) for l in error.get('loc', [])])
                msg = error.get('msg', 'Invalid value')
                errors.append(f"{loc}: {msg}")
        else:
            errors.append(str(e))
        return False, errors
