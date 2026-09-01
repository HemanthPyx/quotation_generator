import os
from pathlib import Path
from config import settings

def ensure_storage_dirs() -> None:
    Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.QUOTATIONS_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.LOGOS_PATH).mkdir(parents=True, exist_ok=True)

def save_quotation_file(content: bytes, quotation_number: str, extension: str) -> str:
    ensure_storage_dirs()
    file_path = Path(settings.QUOTATIONS_PATH) / f"{quotation_number}.{extension}"
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path)

def get_quotation_file(file_path: str) -> bytes | None:
    path = Path(file_path)
    if path.exists() and path.is_file():
        with open(path, "rb") as f:
            return f.read()
    return None

def delete_quotation_files(quotation_number: str) -> None:
    base_path = Path(settings.QUOTATIONS_PATH)
    for ext in ['pdf', 'png', 'jpeg', 'jpg']:
        file_path = base_path / f"{quotation_number}.{ext}"
        if file_path.exists():
            file_path.unlink()
