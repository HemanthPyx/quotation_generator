import os
import shutil
from pathlib import Path
from models.settings import CompanySettings
from config import settings

def get_settings(db) -> CompanySettings | None:
    return db.query(CompanySettings).first()

def save_settings(db, data: dict) -> CompanySettings:
    settings_obj = get_settings(db)
    if settings_obj:
        for key, value in data.items():
            setattr(settings_obj, key, value)
    else:
        settings_obj = CompanySettings(**data)
        db.add(settings_obj)
    db.commit()
    db.refresh(settings_obj)
    return settings_obj

def save_logo(uploaded_file) -> str:
    logos_dir = Path(settings.LOGOS_PATH)
    logos_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = logos_dir / uploaded_file.name
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file, buffer)
    
    return str(file_path)
