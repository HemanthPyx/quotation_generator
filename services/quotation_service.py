from datetime import datetime
from sqlalchemy.orm import joinedload
from models.quotation import Quotation, QuotationItem
from models.customer import Customer
import utils.quotation_number
from services.calculation_service import calculate_totals

def _get_or_create_customer(db, customer_data: dict) -> Customer:
    if 'id' in customer_data and customer_data['id']:
        customer = db.query(Customer).filter(Customer.id == customer_data['id']).first()
        if customer:
            return customer
            
    customer = db.query(Customer).filter(
        Customer.email == customer_data.get('email')
    ).first()
    
    if not customer:
        customer = Customer(**customer_data)
        db.add(customer)
        db.flush()
    return customer

def create_quotation(db, quotation_data: dict) -> Quotation:
    customer_data = quotation_data.pop('customer', {})
    items_data = quotation_data.pop('items', [])
    
    customer = _get_or_create_customer(db, customer_data)
    
    quotation_number = utils.quotation_number.generate_quotation_number(db)
    
    totals = calculate_totals(items_data)
    
    quotation = Quotation(
        quotation_number=quotation_number,
        customer_id=customer.id,
        subtotal=totals['subtotal'],
        discount_total=totals['discount_total'],
        grand_total=totals['grand_total'],
        **quotation_data
    )
    db.add(quotation)
    db.flush()
    
    for i, item_data in enumerate(items_data):
        item = QuotationItem(
            quotation_id=quotation.id,
            sort_order=i,
            **item_data
        )
        db.add(item)
        
    db.commit()
    db.refresh(quotation)
    return quotation

def update_quotation(db, quotation_id: int, quotation_data: dict) -> Quotation:
    quotation = get_quotation(db, quotation_id)
    if not quotation:
        return None
        
    items_data = quotation_data.pop('items', None)
    
    for key, value in quotation_data.items():
        setattr(quotation, key, value)
        
    if items_data is not None:
        for item in quotation.items:
            db.delete(item)
        db.flush()
        
        totals = calculate_totals(items_data)
        quotation.subtotal = totals['subtotal']
        quotation.discount_total = totals['discount_total']
        quotation.grand_total = totals['grand_total']
        
        for i, item_data in enumerate(items_data):
            item = QuotationItem(
                quotation_id=quotation.id,
                sort_order=i,
                **item_data
            )
            db.add(item)
            
    db.commit()
    db.refresh(quotation)
    return quotation

def get_quotation(db, quotation_id: int) -> Quotation | None:
    return db.query(Quotation).options(
        joinedload(Quotation.customer),
        joinedload(Quotation.items)
    ).filter(Quotation.id == quotation_id).first()

def get_quotation_by_number(db, quotation_number: str) -> Quotation | None:
    return db.query(Quotation).options(
        joinedload(Quotation.customer),
        joinedload(Quotation.items)
    ).filter(Quotation.quotation_number == quotation_number).first()

def list_quotations(db, status: str = None, limit: int = 50, offset: int = 0) -> list[Quotation]:
    query = db.query(Quotation).options(
        joinedload(Quotation.customer),
        joinedload(Quotation.items)
    )
    if status:
        query = query.filter(Quotation.status == status)
    return query.order_by(Quotation.created_at.desc()).offset(offset).limit(limit).all()

def search_quotations(db, query: str) -> list[Quotation]:
    search_term = f"%{query}%"
    return db.query(Quotation).join(Customer).options(
        joinedload(Quotation.customer),
        joinedload(Quotation.items)
    ).filter(
        (Quotation.quotation_number.ilike(search_term)) |
        (Customer.name.ilike(search_term)) |
        (Customer.company_name.ilike(search_term)) |
        (Customer.phone.ilike(search_term))
    ).order_by(Quotation.created_at.desc()).all()

def delete_quotation(db, quotation_id: int) -> bool:
    quotation = get_quotation(db, quotation_id)
    if quotation:
        from services.file_service import delete_quotation_files
        delete_quotation_files(quotation.quotation_number)
        db.delete(quotation)
        db.commit()
        return True
    return False

def duplicate_quotation(db, quotation_id: int) -> Quotation:
    source = get_quotation(db, quotation_id)
    if not source:
        return None
        
    quotation_number = utils.quotation_number.generate_quotation_number(db)
    
    from datetime import timedelta
    today = datetime.now().date()
    # Calculate validity period from source quotation
    if source.quotation_date and source.valid_until:
        validity_days = (source.valid_until - source.quotation_date).days
    else:
        validity_days = 15
    
    new_quotation = Quotation(
        quotation_number=quotation_number,
        customer_id=source.customer_id,
        quotation_date=today,
        valid_until=today + timedelta(days=validity_days),
        project_type=source.project_type,
        project_description=source.project_description,
        subtotal=source.subtotal,
        discount_total=source.discount_total,
        grand_total=source.grand_total,
        delivery_time=source.delivery_time,
        payment_terms=source.payment_terms,
        notes=source.notes,
        terms_conditions=source.terms_conditions,
        template_name=source.template_name,
        status='Draft'
    )
    db.add(new_quotation)
    db.flush()
    
    for item in source.items:
        new_item = QuotationItem(
            quotation_id=new_quotation.id,
            service_name=item.service_name,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount=item.discount,
            amount=item.amount,
            sort_order=item.sort_order
        )
        db.add(new_item)
        
    db.commit()
    db.refresh(new_quotation)
    return new_quotation

def save_draft(db, quotation_data: dict) -> Quotation:
    quotation_data['status'] = 'Draft'
    return create_quotation(db, quotation_data)

def update_draft(db, quotation_id: int, quotation_data: dict) -> Quotation:
    quotation_data['status'] = 'Draft'
    return update_quotation(db, quotation_id, quotation_data)

def get_dashboard_stats(db) -> dict:
    total_quotations = db.query(Quotation).count()
    draft_count = db.query(Quotation).filter(Quotation.status == 'Draft').count()
    generated_count = db.query(Quotation).filter(Quotation.status == 'Generated').count()
    
    generated_quots = db.query(Quotation).filter(Quotation.status == 'Generated').all()
    total_value = sum(q.grand_total for q in generated_quots if q.grand_total)
    
    return {
        'total_quotations': total_quotations,
        'draft_count': draft_count,
        'generated_count': generated_count,
        'total_value': float(total_value) if total_value else 0.0
    }

def get_recent_quotations(db, limit: int = 10) -> list[Quotation]:
    return list_quotations(db, limit=limit)
