from django.db import models


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    CATEGORY_CHOICES = [
        ('phishing', 'Phishing'),
        ('romance', 'Romance Scam'),
        ('financial', 'Financial Fraud'),
        ('identity', 'Identity Theft'),
        ('malware', 'Malware'),
        ('vishing', 'Vishing/Smishing'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    related_entities = models.ManyToManyField(
        'entities.Entity',
        blank=True,
        related_name='alerts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.severity})'
