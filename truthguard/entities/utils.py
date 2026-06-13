import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def detect_entity_type(value):
    value = value.strip()
    if not value:
        return None

    if re.match(r'^[\d\s\-\+\(\)]{7,20}$', value.replace(' ', '')):
        return 'phone'

    try:
        validate_email(value)
        return 'email'
    except ValidationError:
        pass

    if re.match(
        r'^(https?://)?[\w\-]+(\.[\w\-]+)+[\w\-.,@?^=%&:/~+#]*$',
        value,
        re.IGNORECASE,
    ):
        return 'website'

    return None


def normalize_value(entity_type, value):
    value = value.strip()
    if entity_type == 'phone':
        return re.sub(r'[^\d+]', '', value)
    if entity_type == 'email':
        return value.lower()
    if entity_type == 'website':
        if not value.startswith(('http://', 'https://')):
            return f'https://{value}'
        return value.lower()
    return value
