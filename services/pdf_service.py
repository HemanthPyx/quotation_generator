from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

DARK_TEAL = HexColor("#145050")
LIGHT_GRAY = HexColor("#F0F0F0")

def format_currency(amount):
    if amount is None:
        return "Rs. 0.00"
    return f"Rs. {amount:,.2f}"

def generate_pdf(quotation, company_settings) -> bytes:
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=white,
        spaceAfter=5
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=16,
        textColor=white,
        spaceAfter=5
    )
    desc_style = ParagraphStyle(
        'DescStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        textColor=white
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=white,
        backColor=DARK_TEAL,
        spaceBefore=15,
        spaceAfter=10,
        leftIndent=5,
        rightIndent=5,
        borderPadding=5
    )
    
    normal_style = styles['Normal']
    normal_style.fontName = 'Helvetica'
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=normal_style,
        bulletIndent=10,
        leftIndent=20,
        spaceAfter=3
    )

    story = []

    header_data = [
        [Paragraph(f"{quotation.project_type or 'WEBSITE DEVELOPMENT'}", title_style)],
        [Paragraph("QUOTATION", subtitle_style)],
        [Paragraph(f"{quotation.project_description or ''}", desc_style)]
    ]
    
    header_table = Table(header_data, colWidths=[180*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_TEAL),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10*mm))
    
    q_date = quotation.quotation_date.strftime("%d %B %Y") if hasattr(quotation.quotation_date, 'strftime') else quotation.quotation_date
    info_data = [
        [Paragraph(f"<b>Quotation No.</b> {quotation.quotation_number}", ParagraphStyle('RightBold', parent=normal_style, alignment=TA_RIGHT))],
        [Paragraph(f"<b>Date</b> {q_date}", ParagraphStyle('RightNormal', parent=normal_style, alignment=TA_RIGHT))]
    ]
    info_table = Table(info_data, colWidths=[180*mm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10*mm))
    
    cust = quotation.customer
    cs = company_settings
    
    prepared_for = [
        Paragraph("<b>Prepared For:</b>", bold_style),
        Paragraph(f"Client Name: {cust.name if cust else ''}", normal_style),
        Paragraph(f"Business / Brand: {cust.company_name if cust else ''}", normal_style),
        Paragraph(f"Contact: {cust.phone if cust else ''} / {cust.email if cust else ''}", normal_style)
    ]
    
    prepared_by = [
        Paragraph("<b>Prepared By:</b>", bold_style),
        Paragraph(f"{cs.company_name if cs else ''}", normal_style),
        Paragraph(f"{cs.tagline if cs else ''}", normal_style),
        Paragraph(f"Phone: {cs.phone if cs else ''} | Email: {cs.email if cs else ''}", normal_style),
        Paragraph(f"Website: {cs.website if cs else ''}", normal_style)
    ]
    
    parties_data = [[prepared_for, prepared_by]]
    parties_table = Table(parties_data, colWidths=[90*mm, 90*mm])
    parties_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 15*mm))
    
    first_service = quotation.items[0].service_name if quotation.items else "Service"
    package_title = f"{first_service} Package - {format_currency(quotation.grand_total)}"
    story.append(Paragraph(package_title, ParagraphStyle('PackageTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14)))
    story.append(Spacer(1, 5*mm))
    
    table_data = [["Service / Deliverable", "Details", "Price"]]
    
    for item in quotation.items:
        amount_str = format_currency(item.amount) if item.amount > 0 else "Included"
        if item.amount == 0 and "actual cost" in (item.description or "").lower():
            amount_str = "Charged at actual cost"
            
        table_data.append([
            Paragraph(item.service_name, bold_style),
            Paragraph(item.description or "", normal_style),
            amount_str
        ])
        
    items_table = Table(table_data, colWidths=[50*mm, 100*mm, 30*mm])
    
    table_style = [
        ('BACKGROUND', (0,0), (-1,0), DARK_TEAL),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, black),
        ('BOX', (0,0), (-1,-1), 0.25, black),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]
    
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            table_style.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GRAY))
            
    items_table.setStyle(TableStyle(table_style))
    story.append(items_table)
    story.append(Spacer(1, 5*mm))
    
    totals_data = []
    if quotation.discount_total > 0:
        totals_data.append(["Subtotal:", format_currency(quotation.subtotal)])
        totals_data.append(["Discount:", f"- {format_currency(quotation.discount_total)}"])
        
    totals_data.append(["Estimated Customer Payment:", format_currency(quotation.grand_total)])
    
    totals_table = Table(totals_data, colWidths=[140*mm, 40*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 15*mm))
    
    if quotation.payment_terms:
        story.append(Paragraph("PAYMENT TERMS", section_header_style))
        terms = quotation.payment_terms.split('\n')
        for term in terms:
            if term.strip():
                story.append(Paragraph(f"• {term.strip()}", bullet_style))
        story.append(Spacer(1, 5*mm))
        
    if quotation.delivery_time:
        story.append(Paragraph("DELIVERY & REVISIONS", section_header_style))
        deliveries = quotation.delivery_time.split('\n')
        for delivery in deliveries:
            if delivery.strip():
                story.append(Paragraph(f"• {delivery.strip()}", bullet_style))
        story.append(Spacer(1, 5*mm))
        
    notes_content = []
    if quotation.terms_conditions:
        notes_content.extend(quotation.terms_conditions.split('\n'))
    if quotation.notes:
        notes_content.extend(quotation.notes.split('\n'))
        
    if notes_content:
        story.append(Paragraph("IMPORTANT NOTES", section_header_style))
        for note in notes_content:
            if note.strip():
                story.append(Paragraph(f"• {note.strip()}", bullet_style))
                
    story.append(Spacer(1, 15*mm))
    
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(black)
        canvas.drawString(15*mm, 15*mm, "Thank you for your business!")
        # Calculate validity days from dates
        if quotation.quotation_date and quotation.valid_until:
            validity_days = (quotation.valid_until - quotation.quotation_date).days
        else:
            validity_days = 15
        canvas.drawRightString(A4[0] - 15*mm, 15*mm, f"Quotation valid for {validity_days} days from the date of issue. Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    
    return buffer.getvalue()
