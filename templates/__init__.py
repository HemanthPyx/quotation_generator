TEMPLATES = {
    'professional': {
        'name': 'Professional',
        'description': 'Clean professional quotation template'
    }
}

def get_template_list() -> list[dict]:
    return [{'id': k, **v} for k, v in TEMPLATES.items()]

def get_template_name(key: str) -> str:
    return TEMPLATES.get(key, {}).get('name', key)
