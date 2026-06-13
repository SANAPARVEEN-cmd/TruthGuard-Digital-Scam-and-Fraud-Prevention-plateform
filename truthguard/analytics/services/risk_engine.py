"""
TruthGuard Risk Scoring Engine

Calculates explainable risk scores based on:
- Approved reports
- User reputation
- Pattern matches
- Alert associations
- Historical activity
"""

import re
from datetime import timedelta

from django.utils import timezone

from analytics.models import Pattern
from reports.models import Report


class RiskEngine:
    THREAT_THRESHOLDS = [
        (80, 'critical'),
        (60, 'high'),
        (40, 'medium'),
        (20, 'low'),
        (0, 'safe'),
    ]

    def calculate(self, entity):
        score = 0
        reasons = []

        approved_reports = Report.objects.filter(
            entity=entity,
            report_status='approved',
        )
        approved_count = approved_reports.count()

        if approved_count:
            report_points = min(approved_count * 8, 50)
            score += report_points
            reasons.append(f'{approved_count} approved community report{"s" if approved_count != 1 else ""}')

        pending_count = Report.objects.filter(
            entity=entity,
            report_status='pending',
        ).count()
        if pending_count:
            pending_points = min(pending_count * 3, 15)
            score += pending_points
            reasons.append(f'{pending_count} pending report{"s" if pending_count != 1 else ""} awaiting review')

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
            bonus = min(reputation_bonus, 15)
            score += bonus
            reasons.append('Reports from trusted community members')

        pattern_matches = self._check_patterns(entity)
        if pattern_matches:
            pattern_points = min(len(pattern_matches) * 12, 25)
            score += pattern_points
            for pattern in pattern_matches[:3]:
                reasons.append(f'Pattern match: {pattern.pattern_name}')

        alert_count = entity.alerts.filter(is_active=True).count()
        if alert_count:
            alert_points = min(alert_count * 10, 20)
            score += alert_points
            reasons.append(f'Linked to {alert_count} active fraud alert{"s" if alert_count != 1 else ""}')

        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_reports = approved_reports.filter(created_at__gte=recent_cutoff).count()
        if recent_reports >= 3:
            surge_points = min((recent_reports - 2) * 5, 15)
            score += surge_points
            reasons.append('Recent complaint surge detected')

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

    def _check_patterns(self, entity):
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

    def update_entity(self, entity):
        result = self.calculate(entity)
        entity.risk_score = result['risk_score']
        entity.threat_level = result['threat_level']
        entity.risk_explanation = result['explanation']
        entity.report_count = Report.objects.filter(entity=entity).count()
        entity.save(update_fields=[
            'risk_score', 'threat_level', 'risk_explanation',
            'report_count', 'updated_at',
        ])
        return result


risk_engine = RiskEngine()
