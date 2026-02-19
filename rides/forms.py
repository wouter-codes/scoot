from django import forms
from .models import Rides
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row, Column

class RideSearchForm(forms.ModelForm):
    """Form for searching rides by origin, destination, date, and min passengers."""
    
    min_passengers = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=False,
        label='Passengers',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].required = False
        
        # Set placeholders and hide labels
        self.fields['origin'].widget.attrs['placeholder'] = 'Leaving from'
        self.fields['destination'].widget.attrs['placeholder'] = 'Going to'
        self.fields['date'].widget.attrs['placeholder'] = 'On'
        self.fields['min_passengers'].widget.attrs['placeholder'] = 'Passengers'
        
        # Hide labels
        self.fields['origin'].label = ''
        self.fields['destination'].label = ''
        self.fields['date'].label = ''
        self.fields['min_passengers'].label = ''
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Row(
            Column('origin', css_class='col-12 col-lg-3'),
            Column('destination', css_class='col-12 col-lg-3'),
            Column('date', css_class='col-12 col-lg-2'),
            Column('min_passengers', css_class='col-12 col-lg-2'),
            Column(Submit('submit', 'Search', css_class='btn-signup w-100'), css_class='col-12 col-lg-2'),
        )
    
    class Meta:
        model = Rides
        fields = ['origin', 'destination', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }