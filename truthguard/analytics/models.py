from django.db import models


class Pattern(models.Model):
    pattern_name = models.CharField(max_length=255)
    signature = models.CharField(max_length=500, help_text='Regex or keyword signature')
    description = models.TextField(blank=True)
    risk_weight = models.PositiveIntegerField(default=10)
    related_entities = models.ManyToManyField(
        'entities.Entity',
        blank=True,
        related_name='patterns',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-risk_weight', 'pattern_name']

    def __str__(self):
        return self.pattern_name
