import datetime, re
from django import forms
from django.utils import timezone
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
        """
        Initialize RideSearchForm, set field requirements, placeholders, labels, and crispy form layout.
        """
        super().__init__(*args, **kwargs)
        self.fields['date'].required = False

        # Set placeholders and hide labels
        self.fields['origin'].widget.attrs['placeholder'] = 'Leaving from'
        self.fields['destination'].widget.attrs['placeholder'] = 'Going to'
        self.fields['min_passengers'].widget.attrs['placeholder'] = 'Passengers'

        # Set field labels for accessibility (visually hidden in CSS)
        self.fields['origin'].label = 'Leaving from'
        self.fields['destination'].label = 'Going to'
        self.fields['date'].label = 'Date of travel'
        self.fields['min_passengers'].label = 'Amount of passengers '

        # Make leaving from and going to optional for search form
        self.fields['origin'].required = False
        self.fields['destination'].required = False

        # Initialize crispy form helper and layout
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'search-rides-form'
        self.helper.layout = Layout(
            Row(
                Column('origin', css_class='col-12 col-lg-3'),
                Column('destination', css_class='col-12 col-lg-3'),
                Column('date', css_class='col-12 col-lg-2'),
                Column('min_passengers', css_class='col-12 col-lg-2'),
                Column(Submit('submit', 'Search', css_class='btn-primary search-btn w-100'), css_class='col-12 col-lg-2'),
            )
        )

    def clean_origin(self):
        """
        Validate that origin contains only alphabetic characters and spaces.
        """
        origin = self.cleaned_data.get('origin', '')
        if origin and not re.match(r'^[A-Za-z\s]+$', origin):
            raise forms.ValidationError('Origin must contain only alphabetic characters and spaces.')
        return origin

    def clean_destination(self):
        """
        Validate that destination contains only alphabetic characters and spaces.
        """
        destination = self.cleaned_data.get('destination', '')
        if destination and not re.match(r'^[A-Za-z\s]+$', destination):
            raise forms.ValidationError('Destination must contain only alphabetic characters and spaces.')
        return destination

    def clean_date(self):
        """
        Always set today's date to one hour from now; for other dates, leave time as is.
        """
        date = self.cleaned_data.get('date')
        if not date:
            return date
    
        # if date is today, set time to one hour from now
        if date.date() == timezone.now().date():
            now = timezone.now()
            return now + datetime.timedelta(hours=1)
        else:
            return date

    class Meta:
        model = Rides
        fields = ['origin', 'destination', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class RideForm(forms.ModelForm):
    """Form for creating a new or editing existing ride listing."""
    def clean_origin(self):
        """
        Validate that origin is at least 3 characters and contains only alphabetic characters and spaces.
        """
        origin = self.cleaned_data.get('origin', '')
        if len(origin.strip()) < 3:
            raise forms.ValidationError('Origin must be at least 3 characters.')
        if not re.match(r'^[A-Za-z\s]+$', origin):
            raise forms.ValidationError('Origin must contain only alphabetic characters and spaces.')
        return origin

    def clean_destination(self):
        """
        Validate that destination is at least 3 characters and contains only alphabetic characters and spaces.
        """
        destination = self.cleaned_data.get('destination', '')
        if len(destination.strip()) < 3:
            raise forms.ValidationError('Destination must be at least 3 characters.')
        if not re.match(r'^[A-Za-z\s]+$', destination):
            raise forms.ValidationError('Destination must contain only alphabetic characters and spaces.')
        return destination    

    def clean_date(self):
        """
        Validate that date is provided.
        """
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError('Please select a date and departure time.')
        return date

    def clean_seats_available(self):
        """
        Validate that seats_available is between 1 and 4.
        """
        seats = self.cleaned_data.get('seats_available')
        if seats is None:
            raise forms.ValidationError('Please specify the number of available seats.')
        if seats < 1:
            raise forms.ValidationError('You must offer at least 1 seat.')
        if seats > 4:
            raise forms.ValidationError('You can offer a maximum of 4 seats.')
        return seats

    def __init__(self, *args, **kwargs):
        """
        Initialize RideForm, set field requirements, placeholders, labels, and crispy form layout.
        """
        super().__init__(*args, **kwargs)
        # Set initial date to now rounded down to the nearest 15 minutes, no seconds
        if not self.fields['date'].initial:
            now = timezone.now()
            minute = (now.minute // 15) * 15
            now = now.replace(minute=minute, second=0, microsecond=0)
            self.fields['date'].initial = now
        
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
        """
        Initialize RideRequestForm, set seats_requested choices and crispy form layout.
        """
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
        """
        Initialize RideRequestEditForm, set seats_requested choices and crispy form layout.
        """
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