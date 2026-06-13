import os
import re

from django.core.exceptions import ValidationError


ALLOWED_EVIDENCE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.webp'}
MAX_EVIDENCE_SIZE = 5 * 1024 * 1024


def validate_evidence_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EVIDENCE_EXTENSIONS:
        raise ValidationError(
            f'Unsupported file type. Allowed: {", ".join(sorted(ALLOWED_EVIDENCE_EXTENSIONS))}'
        )
    if file.size > MAX_EVIDENCE_SIZE:
        raise ValidationError('File size must be under 5 MB.')


def normalize_entity_value(entity_type, value):
    value = value.strip()
    if entity_type == 'phone':
        return re.sub(r'[^\d+]', '', value)
    if entity_type == 'email':
        return value.lower()
    if entity_type == 'website':
        if not value.startswith(('http://', 'https://')):
            return f'https://{value}'.lower()
        return value.lower()
    return value
