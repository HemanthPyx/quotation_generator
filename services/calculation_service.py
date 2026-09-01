def calculate_item_amount(quantity: int, unit_price: float, discount: float = 0.0) -> float:
    amount = (quantity * unit_price) - discount
    return max(0.0, amount)

def calculate_totals(items: list[dict]) -> dict:
    subtotal = sum(item.get('quantity', 0) * item.get('unit_price', 0.0) for item in items)
    discount_total = sum(item.get('discount', 0.0) for item in items)
    grand_total = max(0.0, subtotal - discount_total)
    
    return {
        'subtotal': subtotal,
        'discount_total': discount_total,
        'grand_total': grand_total
    }
