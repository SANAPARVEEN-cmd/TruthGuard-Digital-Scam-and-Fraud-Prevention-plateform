from django.conf import settings
from django.db import models

from entities.models import Entity


def evidence_upload_path(instance, filename):
    return f'evidence/{instance.entity.id}/{filename}'


class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
    )
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='reports')
    description = models.TextField()
    evidence = models.FileField(upload_to=evidence_upload_path, blank=True, null=True)
    report_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Report on {self.entity.entity_value} ({self.report_status})'
