import streamlit as st
from database import init_db, SessionLocal
from views.dashboard import render_dashboard
from views.create_quotation import render_create_quotation
from views.quotation_history import render_quotation_history
from views.services import render_services
from views.settings import render_settings
import os

st.set_page_config(
    page_title="Quotation Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "static", "style.css")
try:
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass # CSS not found, continue anyway

# Initialize DB on first run
@st.cache_resource
def setup_db():
    init_db()
    return True

setup_db()

# Sidebar Navigation
st.sidebar.markdown("## 📋 Quotation App")
st.sidebar.markdown("---")

nav_options = [
    "📊 Dashboard",
    "➕ Create Quotation",
    "📋 Quotation History",
    "🔧 Services",
    "⚙️ Settings"
]

if 'current_view' not in st.session_state:
    st.session_state.current_view = "📊 Dashboard"

selection = st.sidebar.radio("Navigation", nav_options, index=nav_options.index(st.session_state.current_view), label_visibility="collapsed")
st.session_state.current_view = selection

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: #94a3b8; font-size: 12px;'>Quotation Generator v1.0<br>© 2026</div>", unsafe_allow_html=True)

# Main Content Area
if selection == "📊 Dashboard":
    render_dashboard()
elif selection == "➕ Create Quotation":
    render_create_quotation()
elif selection == "📋 Quotation History":
    render_quotation_history()
elif selection == "🔧 Services":
    render_services()
elif selection == "⚙️ Settings":
    render_settings()
