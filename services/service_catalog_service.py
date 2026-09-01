from models.service import Service

def get_all_services(db, active_only: bool = True) -> list[Service]:
    query = db.query(Service)
    if active_only:
        query = query.filter(Service.active == True)
    return query.all()

def get_service(db, service_id: int) -> Service | None:
    return db.query(Service).filter(Service.id == service_id).first()

def create_service(db, data: dict) -> Service:
    service = Service(**data)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def update_service(db, service_id: int, data: dict) -> Service:
    service = get_service(db, service_id)
    if service:
        for key, value in data.items():
            setattr(service, key, value)
        db.commit()
        db.refresh(service)
    return service

def deactivate_service(db, service_id: int) -> bool:
    service = get_service(db, service_id)
    if service:
        service.active = False
        db.commit()
        return True
    return False

def activate_service(db, service_id: int) -> bool:
    service = get_service(db, service_id)
    if service:
        service.active = True
        db.commit()
        return True
    return False
