import streamlit as st
from database import SessionLocal
from services.quotation_service import get_dashboard_stats, get_recent_quotations
from utils.helpers import format_currency, format_date_short

def render_dashboard():
    st.title("📊 Dashboard")
    
    db = SessionLocal()
    try:
        stats = get_dashboard_stats(db)
        recent_quotations = get_recent_quotations(db, limit=10)
        
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-card metric-blue">
        <h3>Total Quotations</h3>
        <p>📋 {stats['total_quotations']}</p>
    </div>
    <div class="metric-card metric-amber">
        <h3>Draft</h3>
        <p>📝 {stats['draft_count']}</p>
    </div>
    <div class="metric-card metric-green">
        <h3>Generated</h3>
        <p>✅ {stats['generated_count']}</p>
    </div>
    <div class="metric-card metric-teal">
        <h3>Total Value</h3>
        <p>💰 {format_currency(stats['total_value'])}</p>
    </div>
</div>
""", unsafe_allow_html=True)
        
        st.markdown("### Recent Quotations")
        
        if not recent_quotations:
            st.info("No quotations found. Go to 'Create Quotation' to get started!")
            return
            
        html_table = """
<div class="card table-container">
    <table class="custom-table">
        <thead>
            <tr>
                <th>Quotation #</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>"""
        
        for q in recent_quotations:
            status_class = "badge-generated" if q.status == "Generated" else "badge-draft"
            customer_name = q.customer.name if q.customer else 'N/A'
            html_table += f"""
<tr>
    <td><strong>{q.quotation_number}</strong></td>
    <td>{customer_name}</td>
    <td>{format_date_short(q.quotation_date)}</td>
    <td>{format_currency(q.grand_total)}</td>
    <td><span class="badge {status_class}">{q.status}</span></td>
</tr>
"""
            
        html_table += """
        </tbody>
    </table>
</div>
"""
        st.html(html_table)
    finally:
        db.close()

