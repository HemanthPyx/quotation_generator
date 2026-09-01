from database import SessionLocal, init_db
from models.service import Service

SERVICES = [
    {
        "service_name": "Portfolio Website",
        "default_price": 5000,
        "description": "Responsive portfolio website with up to 5 pages"
    },
    {
        "service_name": "Business Website",
        "default_price": 8000,
        "description": "Professional business website with advanced features"
    },
    {
        "service_name": "Landing Page",
        "default_price": 3500,
        "description": "Single-page landing page optimized for conversions"
    },
    {
        "service_name": "E-commerce Website",
        "default_price": 20000,
        "description": "Full e-commerce website with product management"
    },
    {
        "service_name": "Basic SEO",
        "default_price": 0,
        "description": "On-page SEO setup including meta tags, sitemap, and indexing"
    },
    {
        "service_name": "WhatsApp Integration",
        "default_price": 0,
        "description": "WhatsApp chat and call-to-action integration"
    },
    {
        "service_name": "SSL Certificate",
        "default_price": 0,
        "description": "HTTPS/SSL setup and deployment"
    },
    {
        "service_name": "Extra Page",
        "default_price": 500,
        "description": "Additional page beyond the standard package"
    },
    {
        "service_name": "Website Maintenance",
        "default_price": 1000,
        "description": "Monthly website maintenance and updates"
    },
    {
        "service_name": "Domain Registration",
        "default_price": 0,
        "description": "Domain registration at actual cost"
    },
    {
        "service_name": "Hosting",
        "default_price": 0,
        "description": "Web hosting at actual cost"
    }
]

def seed_services():
    init_db()
    db = SessionLocal()
    try:
        added_count = 0
        for svc_data in SERVICES:
            existing = db.query(Service).filter_by(service_name=svc_data["service_name"]).first()
            if not existing:
                new_service = Service(
                    service_name=svc_data["service_name"],
                    default_price=svc_data["default_price"],
                    description=svc_data["description"]
                )
                db.add(new_service)
                added_count += 1
        
        if added_count > 0:
            db.commit()
            print(f"Successfully seeded {added_count} new services.")
        else:
            print("No new services to seed. All default services already exist.")
            
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_services()
