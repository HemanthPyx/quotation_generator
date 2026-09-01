import streamlit as st
from database import SessionLocal
from services.quotation_service import (
    list_quotations, search_quotations, delete_quotation, duplicate_quotation
)
from utils.helpers import format_currency, format_date_short
import os

def render_quotation_history():
    st.title("📋 Quotation History")
    
    search_query = st.text_input("🔍 Search", placeholder="Search by Quotation ID, Customer Name, Company, Phone...")
    
    db = SessionLocal()
    try:
        if search_query:
            quotations = search_quotations(db, search_query)
        else:
            quotations = list_quotations(db)
            
        if not quotations:
            st.info("No quotations found.")
            return
            
        for q in quotations:
            with st.container():
                status_class = "badge-generated" if q.status == "Generated" else "badge-draft"
                
                html_card = f"""
                <div class="card" style="padding: 15px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: var(--primary);">{q.quotation_number}</h4>
                            <p style="margin: 5px 0 0 0; color: var(--secondary);">
                                <strong>{q.customer.name if q.customer else 'Unknown'}</strong> 
                                {f'({q.customer.company_name})' if q.customer and q.customer.company_name else ''}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <h4 style="margin: 0;">{format_currency(q.grand_total)}</h4>
                            <p style="margin: 5px 0 0 0; font-size: 12px; color: var(--text-muted);">{format_date_short(q.quotation_date)}</p>
                        </div>
                        <div>
                            <span class="badge {status_class}">{q.status}</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                
                with st.popover("⚙️ Actions", use_container_width=True):
                    pc1, pc2 = st.columns(2)
                    if pc1.button("👁️ View", key=f"view_{q.id}", use_container_width=True):
                        st.info(f"Viewing Quotation: {q.quotation_number}")
                    
                    if pc2.button("✏️ Edit", key=f"edit_{q.id}", use_container_width=True):
                        st.session_state.edit_quotation_id = q.id
                        st.session_state.current_view = "➕ Create Quotation"
                        st.rerun()
                        
                    if pc1.button("📋 Duplicate", key=f"dup_{q.id}", use_container_width=True):
                        new_q = duplicate_quotation(db, q.id)
                        st.success(f"Duplicated as {new_q.quotation_number}")
                        st.rerun()
                        
                    if pc2.button("🗑️ Delete", key=f"del_btn_{q.id}", use_container_width=True):
                        st.session_state[f"confirm_del_{q.id}"] = True
                        
                    st.markdown("---")
                    
                    if q.pdf_path and os.path.exists(q.pdf_path):
                        with open(q.pdf_path, "rb") as f:
                            st.download_button("⬇️ Download PDF", f.read(), file_name=os.path.basename(q.pdf_path), mime="application/pdf", key=f"dl_pdf_{q.id}", use_container_width=True)
                    else:
                        st.button("PDF Not Generated", disabled=True, key=f"npdf_{q.id}", use_container_width=True)
                        
                    if q.png_path and os.path.exists(q.png_path):
                        with open(q.png_path, "rb") as f:
                            st.download_button("⬇️ Download PNG", f.read(), file_name=os.path.basename(q.png_path), mime="image/png", key=f"dl_png_{q.id}", use_container_width=True)
                    
                if st.session_state.get(f"confirm_del_{q.id}"):
                    st.warning("Are you sure?")
                    cd1, cd2 = st.columns(2)
                    if cd1.button("Yes", key=f"yes_del_{q.id}"):
                        delete_quotation(db, q.id)
                        st.success("Deleted!")
                        del st.session_state[f"confirm_del_{q.id}"]
                        st.rerun()
                    if cd2.button("No", key=f"no_del_{q.id}"):
                        del st.session_state[f"confirm_del_{q.id}"]
                        st.rerun()
                        
    finally:
        db.close()
