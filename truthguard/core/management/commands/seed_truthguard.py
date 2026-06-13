from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from alerts.models import Alert
from analytics.models import Pattern
from analytics.services.risk_engine import risk_engine
from entities.models import Entity
from reports.models import Report


class Command(BaseCommand):
    help = 'Seed TruthGuard with sample fraud intelligence data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding TruthGuard database...')

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@truthguard.io', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin123)'))

        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@truthguard.io'},
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            if hasattr(demo_user, 'profile'):
                demo_user.profile.reputation_score = 85
                demo_user.profile.verified_status = True
                demo_user.profile.save()

        patterns = [
            ('Phishing URL Pattern', r'(fake|scam|phish|secure-login|verify-account)', 15),
            ('Suspicious TLD', r'\.(xyz|top|click|loan|work)$', 12),
            ('Premium Rate Scam', r'^\+(44|1).{10,}$', 10),
            ('Disposable Email', r'@(tempmail|guerrillamail|mailinator|yopmail)\.', 14),
            ('Crypto Scam', r'(bitcoin|crypto|wallet|investment.*guaranteed)', 18),
        ]
        for name, sig, weight in patterns:
            Pattern.objects.get_or_create(
                pattern_name=name,
                defaults={'signature': sig, 'risk_weight': weight, 'description': f'Detects {name}'},
            )

        entities_data = [
            ('phone', '+15559876543', 'high'),
            ('phone', '+447700900123', 'critical'),
            ('email', 'scam-alert@fake-bank.xyz', 'critical'),
            ('email', 'support@secure-login-verify.com', 'high'),
            ('website', 'https://fake-bank.xyz', 'critical'),
            ('website', 'https://secure-paypal-verify.net', 'high'),
            ('website', 'https://google.com', 'safe'),
            ('email', 'contact@legitimate-corp.com', 'low'),
        ]

        entities = {}
        for etype, value, _ in entities_data:
            entity, _ = Entity.objects.get_or_create(
                entity_type=etype,
                entity_value=value,
            )
            entities[value] = entity

        reports_data = [
            (demo_user, '+15559876543', 'Caller claimed to be IRS demanding immediate payment.'),
            (demo_user, 'scam-alert@fake-bank.xyz', 'Phishing email requesting bank credentials.'),
            (demo_user, 'https://fake-bank.xyz', 'Fake banking website collecting login details.'),
            (demo_user, '+447700900123', 'Romance scam phone number reported by multiple victims.'),
            (demo_user, 'support@secure-login-verify.com', 'Spoofed support email with malicious link.'),
            (demo_user, 'https://secure-paypal-verify.net', 'PayPal phishing site detected.'),
        ]

        for reporter, entity_value, description in reports_data:
            entity = entities[entity_value]
            Report.objects.get_or_create(
                reporter=reporter,
                entity=entity,
                description=description,
                defaults={'report_status': 'approved'},
            )

        alerts_data = [
            ('Major Phishing Campaign Detected', 'critical', 'phishing',
             'Coordinated phishing attack targeting financial institutions with 15K+ suspicious domains.'),
            ('Romance Scam Network Exposed', 'high', 'romance',
             'Fraud investigation uncovered a network of 200+ accounts operating romance scams.'),
            ('Malware Distribution Campaign', 'high', 'malware',
             'Detection of malware delivery infrastructure with compromised domains.'),
            ('Data Breach - 50K Records Exposed', 'medium', 'identity',
             'Compromised e-commerce platform leaked customer emails and phone numbers.'),
            ('Vishing Surge Reported', 'medium', 'vishing',
             'Increase in voice phishing calls impersonating government agencies.'),
        ]

        for title, severity, category, description in alerts_data:
            alert, _ = Alert.objects.get_or_create(
                title=title,
                defaults={'severity': severity, 'category': category, 'description': description},
            )
            if 'fake-bank' in title.lower() or 'phishing' in title.lower():
                alert.related_entities.add(entities['https://fake-bank.xyz'])
                alert.related_entities.add(entities['scam-alert@fake-bank.xyz'])

        for entity in Entity.objects.all():
            risk_engine.update_entity(entity)

        self.stdout.write(self.style.SUCCESS('TruthGuard seed data created successfully!'))
