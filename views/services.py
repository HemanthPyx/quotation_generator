import streamlit as st
from database import SessionLocal
from services.service_catalog_service import (
    get_all_services, create_service, update_service, 
    deactivate_service, activate_service
)
from utils.helpers import format_currency

def render_services():
    st.title("🔧 Service Catalog")
    
    db = SessionLocal()
    try:
        with st.expander("➕ Add New Service", expanded=False):
            with st.form("add_service_form"):
                col1, col2 = st.columns(2)
                s_name = col1.text_input("Service Name*")
                s_price = col2.number_input("Default Price*", min_value=0.0, step=100.0)
                s_desc = st.text_area("Description")
                
                if st.form_submit_button("Submit", type="primary"):
                    if not s_name:
                        st.error("Service Name is required.")
                    else:
                        create_service(db, {
                            'service_name': s_name,
                            'description': s_desc,
                            'default_price': s_price
                        })
                        st.success(f"Service '{s_name}' added!")
                        st.rerun()
                        
        st.markdown("### Existing Services")
        services = get_all_services(db, active_only=False)
        
        if not services:
            st.info("No services found.")
            return
            
        for s in services:
            with st.container():
                status_color = "var(--success)" if s.active else "var(--danger)"
                status_text = "Active" if s.active else "Inactive"
                
                st.markdown(f"""
                <div class="card" style="padding: 15px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h4 style="margin: 0; color: var(--primary);">{s.service_name}</h4>
                            <p style="margin: 5px 0 0 0; color: var(--secondary); font-size: 14px;">{s.description or 'No description'}</p>
                        </div>
                        <div style="text-align: right;">
                            <h4 style="margin: 0;">{format_currency(s.default_price)}</h4>
                            <span style="color: {status_color}; font-size: 12px; font-weight: bold;">● {status_text}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 5])
                if s.active:
                    if c1.button("Deactivate", key=f"deact_{s.id}"):
                        deactivate_service(db, s.id)
                        st.rerun()
                else:
                    if c1.button("Activate", key=f"act_{s.id}"):
                        activate_service(db, s.id)
                        st.rerun()
                        
    finally:
        db.close()
