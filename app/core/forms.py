from django import forms
from .models import BodyAnalysis

class BodyAnalysisForm(forms.ModelForm):
    class Meta:
        model = BodyAnalysis
        exclude = ['user', 'created_at']
        widgets = {
            'gender': forms.RadioSelect(attrs={'class': 'form-check-inline'}),
            'activity_level': forms.Select(attrs={'class': 'form-select'}),
        }
