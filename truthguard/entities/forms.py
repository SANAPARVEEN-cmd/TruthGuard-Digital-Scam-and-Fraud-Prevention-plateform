from django import forms

from entities.utils import detect_entity_type


class SearchForm(forms.Form):
    query = forms.CharField(max_length=500, label='Entity to verify')

    def clean_query(self):
        query = self.cleaned_data['query'].strip()
        if not query:
            raise forms.ValidationError('Please enter a phone number, email, or website.')
        return query

    def get_entity_type(self):
        return detect_entity_type(self.cleaned_data.get('query', ''))
