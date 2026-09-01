import streamlit as st
from database import SessionLocal
from services.settings_service import get_settings, save_settings, save_logo
import os

def render_settings():
    st.title("⚙️ Company Settings")
    
    if st.session_state.pop('settings_saved', False):
        st.success("Settings saved successfully!")
    
    db = SessionLocal()
    try:
        settings = get_settings(db)
        
        init_data = {
            'company_name': settings.company_name if settings else '',
            'tagline': settings.tagline if settings else '',
            'phone': settings.phone if settings else '',
            'email': settings.email if settings else '',
            'website': settings.website if settings else '',
            'address': settings.address if settings else '',
            'gst_number': settings.gst_number if settings else '',
            'default_payment_terms': settings.default_payment_terms if settings else '',
            'default_delivery_terms': settings.default_delivery_terms if settings else '',
            'default_validity_days': settings.default_validity_days if settings else 30,
        }
        
        with st.form("settings_form"):
            st.markdown("### General Information")
            c1, c2 = st.columns(2)
            comp_name = c1.text_input("Company / Business Name*", value=init_data['company_name'])
            tagline = c2.text_input("Tagline", value=init_data['tagline'])
            
            c3, c4 = st.columns(2)
            phone = c3.text_input("Phone", value=init_data['phone'])
            email = c4.text_input("Email", value=init_data['email'])
            
            c5, c6 = st.columns(2)
            website = c5.text_input("Website", value=init_data['website'])
            gst = c6.text_input("GST Number", value=init_data['gst_number'])
            
            address = st.text_area("Address", value=init_data['address'])
            
            st.markdown("### Default Defaults")
            pay_terms = st.text_area("Default Payment Terms", value=init_data['default_payment_terms'])
            del_terms = st.text_area("Default Delivery Terms", value=init_data['default_delivery_terms'])
            val_days = st.number_input("Default Quotation Validity (days)", min_value=1, value=init_data['default_validity_days'])
            
            logo_file = st.file_uploader("Upload Company Logo (PNG, JPG)", type=['png', 'jpg', 'jpeg'])
            
            if settings and settings.logo_path and os.path.exists(settings.logo_path):
                st.image(settings.logo_path, width=150, caption="Current Logo")
                
            submitted = st.form_submit_button("💾 Save Settings", type="primary")
            
            if submitted:
                if not comp_name:
                    st.error("Company Name is required.")
                else:
                    data = {
                        'company_name': comp_name,
                        'tagline': tagline,
                        'phone': phone,
                        'email': email,
                        'website': website,
                        'address': address,
                        'gst_number': gst,
                        'default_payment_terms': pay_terms,
                        'default_delivery_terms': del_terms,
                        'default_validity_days': val_days
                    }
                    save_settings(db, data)
                    
                    if logo_file:
                        save_logo(logo_file)
                        
                    st.session_state['settings_saved'] = True
                    st.rerun()
                    
    finally:
        db.close()
