from django.db import models


class Entity(models.Model):
    ENTITY_TYPES = [
        ('phone', 'Phone Number'),
        ('email', 'Email Address'),
        ('website', 'Website URL'),
    ]

    THREAT_LEVELS = [
        ('safe', 'Safe'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('monitoring', 'Under Monitoring'),
        ('blocked', 'Blocked'),
        ('cleared', 'Cleared'),
    ]

    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_value = models.CharField(max_length=500, unique=True, db_index=True)
    risk_score = models.PositiveIntegerField(default=0)
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS, default='safe')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    report_count = models.PositiveIntegerField(default=0)
    risk_explanation = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-risk_score', '-updated_at']
        verbose_name_plural = 'entities'

    def __str__(self):
        return f'{self.entity_value} ({self.threat_level})'

    @property
    def threat_level_display_class(self):
        return self.threat_level
