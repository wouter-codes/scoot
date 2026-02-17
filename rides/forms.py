from django import forms
from .models import Rides

class RideSearchForm(forms.ModelForm):
    """Form for searching rides by origin, destination, date, and passengers."""
    
    passengers = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'How many?',
            'value': '1'
        })
    )
    
    class Meta:
        model = Rides
        fields = ['origin', 'destination', 'date']
        widgets = {
            'origin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where from?',
                'required': False
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where to?',
                'required': False
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': False
            }),
        }
