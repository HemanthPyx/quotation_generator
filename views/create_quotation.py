import streamlit as st
from database import SessionLocal
from services.quotation_service import (
    create_quotation, update_quotation, get_quotation, 
    save_draft, update_draft
)
from services.service_catalog_service import get_all_services
from services.settings_service import get_settings
from services.calculation_service import calculate_item_amount, calculate_totals
from services.pdf_service import generate_pdf
from services.image_service import generate_png, generate_jpeg
from services.file_service import save_quotation_file
from utils.helpers import format_currency
from datetime import datetime
import os

def render_create_quotation():
    edit_id = st.session_state.get('edit_quotation_id', None)
    
    st.title("✏️ Edit Quotation" if edit_id else "➕ Create Quotation")
    
    db = SessionLocal()
    try:
        settings = get_settings(db)
        services = get_all_services(db, active_only=True)
        
        # Initialize session state for items if not present
        if 'quotation_items' not in st.session_state:
            st.session_state.quotation_items = []
            
            default_payment_terms = "50% advance to start the project.\n 50% before final deployment / handover.\n Domain and hosting are payable separately at actual cost."
            default_delivery_time = "Estimated delivery: 5-7 working days after receiving required content.\n Two rounds of minor revisions are included.\n Major redesigns or additional pages are quoted separately."
            default_notes = "Domain, premium hosting, premium plugins/templates, paid third-party services, stock assets and ongoing maintenance are not included in the ₹5,000 development fee unless specifically mentioned.\n Basic SEO means on-page and technical setup; search-ranking results are not guaranteed.\n Client is responsible for providing final text, images, logo and other business content required for the website"
            
            st.session_state.quotation_data = {
                'customer_name': '', 'company_name': '', 'phone': '', 'email': '', 'address': '',
                'project_type': '', 'project_description': '',
                'payment_terms': default_payment_terms,
                'delivery_time': default_delivery_time,
                'notes': default_notes, 'terms_conditions': ''
            }
            
        # If edit mode and first load, populate data
        if edit_id and not st.session_state.get('edit_loaded'):
            q = get_quotation(db, edit_id)
            if q:
                st.session_state.quotation_data = {
                    'customer_name': q.customer.name if q.customer else '',
                    'company_name': q.customer.company_name if q.customer else '',
                    'phone': q.customer.phone if q.customer else '',
                    'email': q.customer.email if q.customer else '',
                    'address': q.customer.address if q.customer else '',
                    'project_type': q.project_type or '',
                    'project_description': q.project_description or '',
                    'payment_terms': q.payment_terms or '',
                    'delivery_time': q.delivery_time or '',
                    'notes': q.notes or '',
                    'terms_conditions': q.terms_conditions or ''
                }
                st.session_state.quotation_items = [
                    {
                        'service_name': i.service_name,
                        'description': i.description or '',
                        'quantity': i.quantity,
                        'unit_price': float(i.unit_price),
                        'discount': float(i.discount)
                    } for i in q.items
                ]
                st.session_state.edit_loaded = True
                
        # --- UI Sections ---
        with st.expander("👤 Customer Details", expanded=True):
            col1, col2 = st.columns(2)
            cust_name = col1.text_input("Customer Name*", value=st.session_state.quotation_data['customer_name'])
            comp_name = col2.text_input("Company Name", value=st.session_state.quotation_data['company_name'])
            phone = col1.text_input("Phone", value=st.session_state.quotation_data['phone'])
            email = col2.text_input("Email", value=st.session_state.quotation_data['email'])
            address = st.text_area("Address", value=st.session_state.quotation_data['address'])
            
        with st.expander("📁 Project Details", expanded=True):
            proj_type = st.text_input("Project / Website Type", value=st.session_state.quotation_data['project_type'])
            proj_desc = st.text_area("Project Description", value=st.session_state.quotation_data['project_description'])
            
        st.markdown("### 🛒 Quotation Items")
        
        # Quick Add from Catalog
        cat_col1, cat_col2 = st.columns([3, 1])
        service_options = [s.service_name for s in services]
        selected_services = cat_col1.multiselect("Quick Add from Catalog", service_options)
        if cat_col2.button("Add Selected"):
            if selected_services:
                for sel in selected_services:
                    svc = next((s for s in services if s.service_name == sel), None)
                    if svc:
                        st.session_state.quotation_items.append({
                            'service_name': svc.service_name,
                            'description': svc.description or '',
                            'quantity': 1,
                            'unit_price': float(svc.default_price),
                            'discount': 0.0
                        })
                st.rerun()
                    
        # Items Table
        for idx, item in enumerate(st.session_state.quotation_items):
            with st.container():
                st.markdown(f"**Item {idx+1}**")
                c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 3, 1, 1.5, 1, 1.5, 0.5])
                
                item['service_name'] = c1.text_input("Service Name", value=item['service_name'], key=f"srv_{idx}")
                item['description'] = c2.text_input("Description", value=item['description'], key=f"desc_{idx}")
                item['quantity'] = c3.number_input("Qty", min_value=1, value=int(item['quantity']), key=f"qty_{idx}")
                item['unit_price'] = c4.number_input("Unit Price", min_value=0.0, value=float(item['unit_price']), step=100.0, key=f"prc_{idx}")
                item['discount'] = c5.number_input("Discount", min_value=0.0, value=float(item['discount']), key=f"dsc_{idx}")
                
                amt = calculate_item_amount(item['quantity'], item['unit_price'], item['discount'])
                c6.text_input("Amount", value=f"₹ {amt:,.2f}", disabled=True, key=f"amt_{idx}")
                
                if c7.button("🗑️", key=f"del_{idx}"):
                    st.session_state.quotation_items.pop(idx)
                    st.rerun()
                    
        if st.button("➕ Add Item"):
            st.session_state.quotation_items.append({'service_name': '', 'description': '', 'quantity': 1, 'unit_price': 0.0, 'discount': 0.0})
            st.rerun()
            
        # Totals
        totals = calculate_totals(st.session_state.quotation_items)
        st.markdown(f"""
        <div style="text-align: right; margin-top: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #64748b;">Subtotal: {format_currency(totals['subtotal'])}</p>
            <p style="margin: 0; color: #ef4444;">Discount: -{format_currency(totals['discount_total'])}</p>
            <h3 style="margin: 10px 0 0 0; color: #0d9488;">Grand Total: {format_currency(totals['grand_total'])}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📜 Terms & Conditions", expanded=False):
            pay_terms = st.text_area("Payment Terms", value=st.session_state.quotation_data['payment_terms'])
            del_time = st.text_area("Delivery Time", value=st.session_state.quotation_data['delivery_time'])
            nts = st.text_area("Notes", value=st.session_state.quotation_data['notes'])
            t_c = st.text_area("Terms & Conditions", value=st.session_state.quotation_data['terms_conditions'])
            
        st.markdown("---")
        
        # Actions
        col_act1, col_act2 = st.columns(2)
        
        from datetime import timedelta
        validity_days = settings.default_validity_days if settings and settings.default_validity_days else 15
        today = datetime.now().date()
        
        data_to_save = {
            'customer': {
                'name': cust_name, 'company_name': comp_name,
                'phone': phone, 'email': email, 'address': address
            },
            'quotation_date': today,
            'valid_until': today + timedelta(days=validity_days),
            'project_type': proj_type, 'project_description': proj_desc,
            'payment_terms': pay_terms, 'delivery_time': del_time,
            'notes': nts, 'terms_conditions': t_c,
            'items': st.session_state.quotation_items,
            'template_name': 'professional'
        }
        
        if col_act1.button("💾 Save Draft", use_container_width=True):
            if not cust_name:
                st.error("Customer Name is required.")
            else:
                if edit_id:
                    update_draft(db, edit_id, data_to_save)
                    st.success("Draft updated successfully!")
                else:
                    save_draft(db, data_to_save)
                    st.success("Draft saved successfully!")
                    
        if col_act2.button("👁️ Generate Preview", type="primary", use_container_width=True):
            if not cust_name:
                st.error("Customer Name is required.")
            elif not st.session_state.quotation_items:
                st.error("Add at least one item.")
            else:
                st.session_state.show_preview = True
                
        if st.session_state.get('show_preview'):
            st.markdown("### 📄 Preview")
            html_preview = f"""
<div class="quotation-preview">
    <div class="preview-header">
        <h2>QUOTATION</h2>
        <div style="text-align: right;">
            <strong>{settings.company_name if settings else 'Company Name'}</strong><br>
            {settings.phone if settings else ''}<br>
            {settings.email if settings else ''}
        </div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <div>
            <h4 style="margin-bottom: 5px; color: var(--secondary);">Bill To:</h4>
            <strong>{cust_name}</strong><br>
            {comp_name}<br>
            {address}
        </div>
        <div style="text-align: right;">
            <strong>Date:</strong> {datetime.now().strftime('%d %B %Y')}<br>
        </div>
    </div>
    
    <table class="custom-table">
        <thead>
            <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {"".join([f"<tr><td><strong>{i['service_name']}</strong><br><small style='color: #64748b;'>{i['description']}</small></td><td>{i['quantity']}</td><td>{format_currency(i['unit_price'])}</td><td>{format_currency(calculate_item_amount(i['quantity'], i['unit_price'], i['discount']))}</td></tr>" for i in st.session_state.quotation_items])}
        </tbody>
    </table>
    
    <div class="preview-totals">
        <p>Subtotal: <strong>{format_currency(totals['subtotal'])}</strong></p>
        <p>Discount: <strong>-{format_currency(totals['discount_total'])}</strong></p>
        <h3 style="color: var(--primary);">Grand Total: {format_currency(totals['grand_total'])}</h3>
    </div>
</div>
"""
            st.html(html_preview)
            
            if st.button("🚀 Generate & Download"):
                with st.spinner("Generating PDF and files..."):
                    if edit_id:
                        q = update_quotation(db, edit_id, data_to_save)
                    else:
                        q = create_quotation(db, data_to_save)
                    
                    pdf_bytes = generate_pdf(q, settings)
                    q.pdf_path = save_quotation_file(pdf_bytes, q.quotation_number, 'pdf')
                    
                    try:
                        png_bytes = generate_png(pdf_bytes)
                        q.png_path = save_quotation_file(png_bytes, q.quotation_number, 'png')
                    except Exception as e:
                        print(f"PNG generation failed: {e}")
                        
                    try:
                        jpeg_bytes = generate_jpeg(pdf_bytes)
                        q.jpeg_path = save_quotation_file(jpeg_bytes, q.quotation_number, 'jpeg')
                    except Exception as e:
                        print(f"JPEG generation failed: {e}")
                        
                    q.status = 'Generated'
                    db.commit()
                    
                    st.success(f"Quotation {q.quotation_number} generated successfully!")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.download_button("⬇️ Download PDF", pdf_bytes, file_name=f"{q.quotation_number}.pdf", mime="application/pdf", type="primary")
                    if q.png_path and os.path.exists(q.png_path):
                        with open(q.png_path, "rb") as f:
                            c2.download_button("⬇️ Download PNG", f.read(), file_name=f"{q.quotation_number}.png", mime="image/png")
                    if q.jpeg_path and os.path.exists(q.jpeg_path):
                        with open(q.jpeg_path, "rb") as f:
                            c3.download_button("⬇️ Download JPEG", f.read(), file_name=f"{q.quotation_number}.jpg", mime="image/jpeg")
                            
                    # Reset after generation
                    if 'edit_quotation_id' in st.session_state:
                        del st.session_state['edit_quotation_id']
                    if 'edit_loaded' in st.session_state:
                        del st.session_state['edit_loaded']
                    st.session_state.quotation_items = []
                    del st.session_state['show_preview']
    finally:
        db.close()
