import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "quotation_generator")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password_here")
        
        # Try to get from Streamlit secrets first (for Streamlit Cloud deployment)
        db_url = None
        try:
            import streamlit as st
            if "DATABASE_URL" in st.secrets:
                db_url = st.secrets["DATABASE_URL"]
        except Exception:
            pass
            
        # Fallback to local environment variable if not in secrets
        if not db_url:
            db_url = os.getenv("DATABASE_URL")
            
        if db_url:
            db_url = db_url.strip().strip('"').strip("'")
            # SQLAlchemy requires 'postgresql://' instead of 'postgres://'
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            self.DATABASE_URL = db_url
        else:
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        self.STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
        self.QUOTATIONS_PATH = self.STORAGE_PATH / "quotations"
        self.LOGOS_PATH = self.STORAGE_PATH / "logos"
        
        self.QUOTATIONS_PATH.mkdir(parents=True, exist_ok=True)
        self.LOGOS_PATH.mkdir(parents=True, exist_ok=True)

settings = Settings()
