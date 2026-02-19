from django import forms
from .models import Rides
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class RideSearchForm(forms.ModelForm):
    """Form for searching rides by origin, destination, date, and min passengers."""
    
    min_passengers = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        help_text='Minimum seats needed'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.add_input(Submit('submit', 'Search Rides', css_class='btn-signup w-100'))
    
    class Meta:
        model = Rides
        fields = ['origin', 'destination', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }