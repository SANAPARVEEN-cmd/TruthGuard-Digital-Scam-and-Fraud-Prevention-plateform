from django import forms

from core.validators import validate_evidence_file
from entities.models import Entity
from entities.utils import normalize_value


class ReportForm(forms.Form):
    entity_type = forms.ChoiceField(choices=Entity.ENTITY_TYPES)
    entity_value = forms.CharField(max_length=500)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-textarea'}))
    evidence = forms.FileField(required=False)

    def clean_entity_value(self):
        entity_type = self.cleaned_data.get('entity_type')
        value = self.cleaned_data['entity_value']
        return normalize_value(entity_type, value)

    def clean_evidence(self):
        evidence = self.cleaned_data.get('evidence')
        if evidence:
            validate_evidence_file(evidence)
        return evidence
