from services.pdf_service import generate_pdf

def render(quotation, company_settings) -> bytes:
    return generate_pdf(quotation, company_settings)
