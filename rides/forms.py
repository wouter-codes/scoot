import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Row, Column, Layout
from .models import Rides, RideRequest

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

        # Set initial date to current year if not provided
        if not self.fields['date'].initial:
            today = datetime.date.today()
            self.fields['date'].initial = today

        # Set placeholders and hide labels
        self.fields['origin'].widget.attrs['placeholder'] = 'Leaving from'
        self.fields['destination'].widget.attrs['placeholder'] = 'Going to'
        self.fields['min_passengers'].widget.attrs['placeholder'] = 'Passengers'

        # Hide labels
        self.fields['origin'].label = ''
        self.fields['destination'].label = ''
        self.fields['date'].label = ''
        self.fields['min_passengers'].label = ''

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('origin', css_class='col-12 col-lg-3'),
                Column('destination', css_class='col-12 col-lg-3'),
                Column('date', css_class='col-12 col-lg-2'),
                Column('min_passengers', css_class='col-12 col-lg-2'),
                Column(Submit('submit', 'Search', css_class='btn-primary search-btn w-100'), css_class='col-12 col-lg-2'),
            )
        )
    
    class Meta:
        model = Rides
        fields = ['origin', 'destination', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class RideCreateForm(forms.ModelForm):
    """Form for creating a new ride listing."""
    def clean_origin(self):
        origin = self.cleaned_data.get('origin', '')
        if len(origin.strip()) < 3:
            raise forms.ValidationError('Origin must be at least 3 characters.')
        return origin

    def clean_destination(self):
        destination = self.cleaned_data.get('destination', '')
        if len(destination.strip()) < 3:
            raise forms.ValidationError('Destination must be at least 3 characters.')
        return destination    
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError('Please select a date and departure time.')
        return date

    def clean_seats_available(self):
        seats = self.cleaned_data.get('seats_available')
        if seats is None:
            raise forms.ValidationError('Please specify the number of available seats.')
        if seats < 1:
            raise forms.ValidationError('You must offer at least 1 seat.')
        if seats > 4:
            raise forms.ValidationError('You can offer a maximum of 4 seats.')
        return seats

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial date to now if not provided
        if not self.fields['date'].initial:
            today = datetime.date.today()
            self.fields['date'].initial = today
        # Set placeholders
        self.fields['origin'].widget.attrs['placeholder'] = 'e.g. Truro'
        self.fields['destination'].widget.attrs['placeholder'] = 'e.g. Falmouth'
        self.fields['pickup_notes'].widget.attrs['placeholder'] = 'e.g. Meet at the train station car park'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
    
    class Meta:
        model = Rides
        fields = ['origin', 'destination', 'date', 'seats_available', 'pickup_notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'pickup_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'origin': 'Pick Up',
            'destination': 'Drop Off',
            'date': 'Date & Departure Time',
            'seats_available': 'Available Seats',
            'pickup_notes': 'Pickup Notes',
        }

class RideRequestForm(forms.ModelForm):
    """Form for submitting a new ride request (number of seats)."""
    seats_requested = forms.ChoiceField(
        label='Seats Requested',
        help_text='Select the number of seats you want to request.'
    )

    def __init__(self, *args, max_seats=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to 4 if not provided
        max_seats = max_seats or 4
        self.fields['seats_requested'].choices = [
            (str(i), str(i)) for i in range(1, max_seats + 1)
        ]
        self.helper = FormHelper()
        self.helper.form_method = 'post'

    class Meta:
        model = RideRequest
        fields = ['seats_requested']

class RideRequestEditForm(forms.ModelForm):
    """Form for editing a ride request (seats_requested)."""
    seats_requested = forms.ChoiceField(
        label='Seats Requested',
        help_text='Select the number of seats you want to request.'
    )

    def __init__(self, *args, max_seats=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to 4 if not provided
        max_seats = max_seats or 4
        self.fields['seats_requested'].choices = [
            (str(i), str(i)) for i in range(1, max_seats + 1)
        ]
        self.helper = FormHelper()
        self.helper.form_method = 'post'

    class Meta:
        model = RideRequest
        fields = ['seats_requested']