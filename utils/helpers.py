import streamlit as st
from datetime import date, datetime

def format_currency(amount) -> str:
    val = float(amount) if amount is not None else 0.0
    is_negative = val < 0
    val = abs(val)
    s = f"{val:,.2f}"
    parts = s.split('.')
    integer_part = parts[0].replace(',', '')
    
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        other = integer_part[:-3]
        other_formatted = ','.join([other[max(0, i-2):i] for i in range(len(other), 0, -2)][::-1])
        integer_part = f"{other_formatted},{last_three}"
    
    formatted_val = f"{integer_part}.{parts[1]}"
    if is_negative:
        return f"-₹ {formatted_val}"
    return f"₹ {formatted_val}"

def format_date(date_obj) -> str:
    if not date_obj:
        return ""
    if isinstance(date_obj, (date, datetime)):
        return date_obj.strftime("%d %B %Y")
    return str(date_obj)

def format_date_short(date_obj) -> str:
    if not date_obj:
        return ""
    if isinstance(date_obj, (date, datetime)):
        return date_obj.strftime("%d-%b-%Y")
    return str(date_obj)

def show_success(message: str):
    st.success(message, icon="✅")

def show_error(message: str):
    st.error(message, icon="🚨")

def show_warning(message: str):
    st.warning(message, icon="⚠️")
