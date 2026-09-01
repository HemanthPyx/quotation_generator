from datetime import datetime
from sqlalchemy import select
from models.quotation import Quotation

def generate_quotation_number(session) -> str:
    current_year = datetime.now().year
    prefix = f"QT-{current_year}-"
    
    stmt = select(Quotation.quotation_number).where(
        Quotation.quotation_number.like(f"{prefix}%")
    ).order_by(Quotation.quotation_number.desc()).limit(1)
    
    result = session.execute(stmt).scalar_one_or_none()
    
    if result:
        sequence_part = result.split('-')[-1]
        next_seq = int(sequence_part) + 1
    else:
        next_seq = 1
        
    return f"{prefix}{next_seq:04d}"
