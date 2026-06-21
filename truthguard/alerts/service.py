"""
TruthGuard Alert Service
Automatically creates / updates alerts based on:
- Report approvals
- Risk score thresholds
- Entity threat level changes
"""

from alerts.models import Alert


def get_category_from_entity(entity, report=None):
    """Map entity type + report description to an alert category."""
    description = (report.description.lower() if report else '')

    if 'phish' in description or 'login' in description or 'password' in description:
        return 'phishing'
    if 'romance' in description or 'dating' in description or 'love' in description:
        return 'romance'
    if 'bank' in description or 'money' in description or 'transfer' in description or 'crypto' in description:
        return 'financial'
    if 'identity' in description or 'personal' in description or 'ssn' in description:
        return 'identity'
    if 'malware' in description or 'virus' in description or 'hack' in description:
        return 'malware'
    if 'call' in description or 'sms' in description or 'text' in description or entity.entity_type == 'phone':
        return 'vishing'
    return 'general'


def get_severity_from_score(risk_score):
    """Map risk score to alert severity."""
    if risk_score >= 80:
        return 'critical'
    if risk_score >= 60:
        return 'high'
    if risk_score >= 40:
        return 'medium'
    return 'low'


def create_or_update_alert(entity, report=None):
    """
    Called after a report is approved or risk score updates.
    - If an active alert already exists for this entity → update it
    - If risk score is high enough → create a new alert
    - If entity drops to safe → deactivate its alerts
    """
    risk_score   = entity.risk_score
    threat_level = entity.threat_level
    severity     = get_severity_from_score(risk_score)
    category     = get_category_from_entity(entity, report)

    # Deactivate alerts if entity is now safe or low
    if threat_level in ('safe', 'low'):
        Alert.objects.filter(
            related_entities=entity,
            is_active=True,
        ).update(is_active=False)
        return None

    # Only create/update alerts for medium risk and above
    if risk_score < 40:
        return None

    # Build alert title and description
    type_label = entity.get_entity_type_display()
    title = f'{severity.upper()} {type_label} Fraud Alert: {entity.entity_value[:60]}'

    description = (
        f'A {type_label.lower()} ({entity.entity_value}) has been flagged as a '
        f'{threat_level} threat with a risk score of {risk_score}/100. '
    )
    if report:
        description += f'Community report: "{report.description[:200]}"'

    # Check if an alert already exists for this entity
    existing = Alert.objects.filter(
        related_entities=entity,
        is_active=True,
    ).first()

    if existing:
        # Update the existing alert with latest info
        existing.title       = title
        existing.description = description
        existing.severity    = severity
        existing.category    = category
        existing.is_active   = True
        existing.save()
        return existing
    else:
        # Create a brand new alert
        alert = Alert.objects.create(
            title=title,
            description=description,
            severity=severity,
            category=category,
            is_active=True,
        )
        alert.related_entities.add(entity)
        return alert


def deactivate_alerts_for_entity(entity):
    """Deactivate all alerts tied to an entity (e.g. when cleared)."""
    Alert.objects.filter(
        related_entities=entity,
        is_active=True,
    ).update(is_active=False)