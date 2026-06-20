"""
TruthGuard Risk Scoring Engine

Calculates explainable risk scores based on:
- Intrinsic analysis (entity value itself — runs even on brand-new entities)
- Approved reports
- User reputation
- Pattern matches (DB)
- Alert associations
- Historical activity
"""

import re
from datetime import timedelta

from django.utils import timezone

from analytics.models import Pattern
from reports.models import Report


# ─── Intrinsic scoring rules (no DB needed) ───────────────────────────────────

# Suspicious TLDs that are heavily abused by scammers
SUSPICIOUS_TLDS = {
    '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.club', '.info',
    '.cc', '.ru', '.pw', '.ws', '.biz', '.link', '.click', '.online',
    '.site', '.live', '.store', '.tech', '.icu', '.monster', '.rest',
}

# Legitimate brands that are commonly typosquatted / impersonated
BRAND_KEYWORDS = [
    'paypal', 'paypa1', 'paypai',
    'amazon', 'amaz0n',
    'google', 'g00gle',
    'apple', 'app1e',
    'microsoft', 'micros0ft',
    'netflix', 'bankofamerica', 'wellsfargo', 'citibank', 'chase',
    'irs', 'tax', 'refund',
    'fedex', 'dhl', 'usps', 'ups',
    'instagram', 'facebook', 'whatsapp', 'telegram',
]

# High-risk words in domains / emails
HIGH_RISK_WORDS = [
    'secure', 'verify', 'login', 'signin', 'account', 'update',
    'confirm', 'alert', 'suspend', 'recover', 'recovery', 'unlock',
    'urgent', 'immediate', 'winner', 'prize', 'reward', 'claim',
    'refund', 'support', 'helpdesk', 'service', 'notify', 'notification',
    'wallet', 'crypto', 'bitcoin', 'investment', 'profit',
    'free', 'gift', 'limited', 'offer', 'deal',
]

# Phone number patterns associated with fraud
SUSPICIOUS_PHONE_PATTERNS = [
    r'^\+?1?900',           # premium rate US
    r'^\+?44700',           # premium rate UK (07xx is real; 0700 is not)
    r'^\+?44191',           # known scam area UK
    r'^\+?(?:234|233|225|221|237)',  # common West African fraud codes
    r'^\+?92',              # Pakistan (romance scam high volume)
    r'^\+?91.*(.)\1{5,}',  # India numbers with repeated digits
    r'^(\d)\1{6,}',         # any number with 7+ repeated digits
]

# Known malicious email providers / free hosts
SUSPICIOUS_EMAIL_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', 'tempmail.com', 'throwam.com',
    'yopmail.com', 'sharklasers.com', 'trashmail.com', 'dispostable.com',
    'maildrop.cc', 'spamgourmet.com', 'fake-profile.com', 'fake-service.com',
}


class RiskEngine:
    THREAT_THRESHOLDS = [
        (80, 'critical'),
        (60, 'high'),
        (40, 'medium'),
        (20, 'low'),
        (0,  'safe'),
    ]

    # ── Public API ─────────────────────────────────────────────────────────────

    def calculate(self, entity):
        score = 0
        reasons = []

        # 1. Intrinsic analysis — works on ANY entity, even brand new ones
        intrinsic_score, intrinsic_reasons = self._intrinsic_analysis(entity)
        score += intrinsic_score
        reasons.extend(intrinsic_reasons)

        # 2. Approved community reports
        approved_reports = Report.objects.filter(
            entity=entity,
            report_status='approved',
        )
        approved_count = approved_reports.count()
        if approved_count:
            report_points = min(approved_count * 8, 40)
            score += report_points
            reasons.append(
                f'{approved_count} approved community report{"s" if approved_count != 1 else ""}'
            )

        # 3. Pending reports (lighter weight)
        pending_count = Report.objects.filter(
            entity=entity,
            report_status='pending',
        ).count()
        if pending_count:
            score += min(pending_count * 3, 12)
            reasons.append(
                f'{pending_count} pending report{"s" if pending_count != 1 else ""} awaiting review'
            )

        # 4. Reporter reputation bonus
        reputation_bonus = 0
        for report in approved_reports.select_related('reporter__profile'):
            if report.reporter and hasattr(report.reporter, 'profile'):
                rep = report.reporter.profile.reputation_score
                if rep >= 80:
                    reputation_bonus += 3
                elif rep >= 60:
                    reputation_bonus += 2
                elif rep >= 40:
                    reputation_bonus += 1
        if reputation_bonus:
            score += min(reputation_bonus, 12)
            reasons.append('Reports from trusted community members')

        # 5. DB pattern matches (your Pattern table)
        pattern_matches = self._check_patterns(entity)
        if pattern_matches:
            score += min(len(pattern_matches) * 10, 20)
            for pattern in pattern_matches[:3]:
                reasons.append(f'Pattern match: {pattern.pattern_name}')

        # 6. Active alerts
        alert_count = entity.alerts.filter(is_active=True).count()
        if alert_count:
            score += min(alert_count * 10, 15)
            reasons.append(
                f'Linked to {alert_count} active fraud alert{"s" if alert_count != 1 else ""}'
            )

        # 7. Recent surge
        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_reports = approved_reports.filter(created_at__gte=recent_cutoff).count()
        if recent_reports >= 3:
            score += min((recent_reports - 2) * 5, 12)
            reasons.append('Recent complaint surge detected')

        # 8. Flagged but unverified
        if entity.report_count > 0 and approved_count == 0:
            score += 5
            reasons.append('Entity flagged but not yet verified by moderators')

        if not reasons:
            reasons.append('No threat indicators found in our database')

        score = min(score, 100)
        threat_level = self._score_to_threat(score)

        return {
            'risk_score': score,
            'threat_level': threat_level,
            'explanation': reasons,
        }

    def update_entity(self, entity):
        result = self.calculate(entity)
        entity.risk_score    = result['risk_score']
        entity.threat_level  = result['threat_level']
        entity.risk_explanation = result['explanation']
        entity.report_count  = Report.objects.filter(entity=entity).count()
        entity.save(update_fields=[
            'risk_score', 'threat_level', 'risk_explanation',
            'report_count', 'updated_at',
        ])
        return result

    # ── Intrinsic Analysis ─────────────────────────────────────────────────────

    def _intrinsic_analysis(self, entity):
        """
        Score the entity value itself — no DB queries needed.
        Returns (score, reasons_list).
        """
        etype = entity.entity_type
        value = entity.entity_value.lower()
        score = 0
        reasons = []

        if etype == 'email':
            s, r = self._analyse_email(value)
        elif etype == 'website':
            s, r = self._analyse_website(value)
        elif etype == 'phone':
            s, r = self._analyse_phone(value)
        else:
            s, r = 0, []

        score += s
        reasons.extend(r)
        return score, reasons

    # ── Email analysis ─────────────────────────────────────────────────────────

    def _analyse_email(self, value):
        score = 0
        reasons = []

        try:
            local, domain = value.rsplit('@', 1)
        except ValueError:
            return 0, []

        # Disposable / known-fake email provider
        if domain in SUSPICIOUS_EMAIL_DOMAINS:
            score += 35
            reasons.append('Disposable or known fraudulent email provider')

        # Brand impersonation in domain
        matched_brands = [b for b in BRAND_KEYWORDS if b in domain]
        if matched_brands:
            score += 30
            reasons.append(f'Brand impersonation detected in email domain ({matched_brands[0]})')

        # High-risk words in local part or domain
        risk_words = [w for w in HIGH_RISK_WORDS if w in local or w in domain]
        if risk_words:
            score += min(len(risk_words) * 8, 24)
            reasons.append(f'High-risk keywords in email: {", ".join(risk_words[:3])}')

        # Suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                score += 20
                reasons.append(f'Suspicious top-level domain ({tld})')
                break

        # Numbers substituting letters (l33t speak — paypa1, g00gle)
        if re.search(r'[a-z][0-9][a-z]|[a-z]{2}[0-9]', domain):
            score += 15
            reasons.append('Possible character substitution (typosquatting) in domain')

        # Excessive hyphens or dots in domain
        if domain.count('-') >= 2:
            score += 12
            reasons.append('Excessive hyphens in email domain — common phishing pattern')

        # Random-looking local part (long string of mixed chars)
        if re.match(r'^[a-z0-9]{12,}$', local) and re.search(r'\d', local):
            score += 8
            reasons.append('Auto-generated looking email address')

        return score, reasons

    # ── Website analysis ───────────────────────────────────────────────────────

    def _analyse_website(self, value):
        score = 0
        reasons = []

        # Strip protocol to get domain + path
        domain_part = re.sub(r'^https?://', '', value)
        domain = domain_part.split('/')[0]

        # HTTP (not HTTPS) — still risky for auth/payment pages
        if value.startswith('http://'):
            score += 15
            reasons.append('Uses insecure HTTP protocol (no SSL)')

        # Brand name in subdomain but real domain is different
        for brand in BRAND_KEYWORDS:
            if brand in domain:
                # Check if it IS the real domain (e.g. paypal.com is fine)
                real_domain_pattern = rf'^(www\.)?{re.escape(brand)}\.(com|net|org)$'
                if not re.match(real_domain_pattern, domain):
                    score += 35
                    reasons.append(f'Brand impersonation: "{brand}" used in fraudulent domain')
                    break

        # Suspicious TLD
        tld_match = re.search(r'(\.[a-z]{2,})$', domain)
        if tld_match and tld_match.group(1) in SUSPICIOUS_TLDS:
            score += 20
            reasons.append(f'High-risk domain extension ({tld_match.group(1)})')

        # Multiple high-risk words in domain
        risk_words = [w for w in HIGH_RISK_WORDS if w in domain]
        if risk_words:
            score += min(len(risk_words) * 10, 30)
            reasons.append(f'High-risk keywords in URL: {", ".join(risk_words[:3])}')

        # Excessive subdomains (e.g. login.secure.paypal.fake.xyz)
        subdomain_count = domain.count('.')
        if subdomain_count >= 3:
            score += 15
            reasons.append(f'Suspicious subdomain depth ({subdomain_count} levels)')

        # Excessive hyphens in domain
        if domain.count('-') >= 2:
            score += 12
            reasons.append('Multiple hyphens in domain — phishing pattern')

        # IP address instead of domain name
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}', domain):
            score += 30
            reasons.append('Website hosted on raw IP address (no domain)')

        # Typosquatting — character substitution
        if re.search(r'[a-z][0-9][a-z]', domain):
            score += 15
            reasons.append('Character substitution detected (typosquatting)')

        # Long random-looking domain
        base = domain.split('.')[0]
        if len(base) > 20 and re.search(r'\d', base):
            score += 10
            reasons.append('Unusually long domain name with numbers — auto-generated pattern')

        return score, reasons

    # ── Phone analysis ─────────────────────────────────────────────────────────

    def _analyse_phone(self, value):
        score = 0
        reasons = []

        # Strip to digits + leading +
        digits = re.sub(r'[^\d+]', '', value)

        # Known high-risk prefixes
        for pattern in SUSPICIOUS_PHONE_PATTERNS:
            if re.match(pattern, digits):
                score += 30
                reasons.append('Phone prefix associated with high fraud activity')
                break

        # Repeated digits (e.g. 555-555-5555, 1234567890 sequences)
        stripped = digits.lstrip('+')
        if re.search(r'(\d)\1{5,}', stripped):
            score += 20
            reasons.append('Suspicious repeating digit pattern')

        # Sequential digits (123456, 987654)
        if re.search(r'(0123|1234|2345|3456|4567|5678|6789|9876|8765)', stripped):
            score += 15
            reasons.append('Sequential digit pattern detected')

        # Very short or very long number
        digit_count = len(stripped)
        if digit_count < 7 or digit_count > 15:
            score += 10
            reasons.append('Phone number length outside valid international range')

        # Premium rate numbers
        if re.match(r'^\+?1?(?:900|976)', digits):
            score += 25
            reasons.append('Premium rate number — commonly used in phone scams')

        return score, reasons

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _check_patterns(self, entity):
        """Check against patterns stored in the DB Pattern table."""
        matches = []
        value = entity.entity_value.lower()
        for pattern in Pattern.objects.filter(is_active=True):
            try:
                if re.search(pattern.signature, value, re.IGNORECASE):
                    matches.append(pattern)
            except re.error:
                if pattern.signature.lower() in value:
                    matches.append(pattern)
        return matches

    def _score_to_threat(self, score):
        for threshold, level in self.THREAT_THRESHOLDS:
            if score >= threshold:
                return level
        return 'safe'


risk_engine = RiskEngine()