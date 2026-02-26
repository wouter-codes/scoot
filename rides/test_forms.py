from django.test import TestCase
from .forms import RideRequestForm, RideSearchForm, RideForm, RideRequestEditForm

# Create your tests here.
class TestRideRequestForm(TestCase):

    def setUp(self):
        """Set up valid and invalid data for testing RideRequestForm."""
        self.valid_data = {
            'seats_requested': 2
        }
        self.invalid_data = {
            'seats_requested': 5  # Invalid: should be between 1 and 4
        }
        self.missing_required = {
            'seats_requested': ''
        }

    def test_form_is_valid(self):
        """Test that form is valid with correct seats_requested value."""
        form = RideRequestForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), msg="Form should be valid with correct data")

    def test_seats_requested_field_validation(self):
        """Test that seats_requested field only accepts valid choices."""
        form = RideRequestForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when seats_requested is out of range")
        self.assertIn('seats_requested', form.errors, msg="seats_requested field should have errors when invalid")

    def test_form_invalid_without_required_fields(self):
        """Test that form is invalid when seats_requested is missing."""
        form = RideRequestForm(data=self.missing_required)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when required fields are missing")
        self.assertIn('seats_requested', form.errors, msg="seats_requested field should have errors when missing")

class TestRideSearchForm(TestCase):
    
    def setUp(self):
        """Set up valid and invalid data for testing RideSearchForm."""
        self.valid_data = {
            'origin': 'Leiden',
            'destination': 'Delft',
            'date': '2099-01-03',
            'min_passengers': 1
        }
        self.invalid_data = {
            'origin': '',
            'destination': '',
            'date': '',
            'min_passengers': ''
        }
        self.partial_data = {
            'origin': 'Leiden',
            'destination': '',
            'date': '',
            'min_passengers': ''
        }

    def test_min_passengers_validation(self):
        """ Test that min_passengers field only accepts valid integers """
        form = RideSearchForm(data={**self.valid_data, 'min_passengers': 'invalid'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when min_passengers is not an integer")
        self.assertIn('min_passengers', form.errors, msg="min_passengers field should have errors when invalid")

    def test_search_form_valid_data(self):
        """ Test that form is valid with correct data """
        form = RideSearchForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), msg="Form should be valid with correct data")

    def test_search_form_invalid_data(self):
        """ Test that form is invalid with incorrect data """
        form = RideSearchForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid with incorrect data")

    def test_search_form_partial_data(self):
        """Test that form is invalid with partial data (only origin) since destination is required."""
        form = RideSearchForm(data=self.partial_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when destination is missing")
        self.assertIn('destination', form.errors, msg="destination field should have errors when missing")

    def test_min_passengers_boundary_values(self):
        """Test min_passengers at its minimum and maximum allowed values."""
        form = RideSearchForm(data={**self.valid_data, 'min_passengers': 1})
        self.assertTrue(form.is_valid(), msg="Form should be valid when min_passengers is 1")

        form = RideSearchForm(data={**self.valid_data, 'min_passengers': 5})
        self.assertTrue(form.is_valid(), msg="Form should be valid when min_passengers is 5")

        form = RideSearchForm(data={**self.valid_data, 'min_passengers': 0})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when min_passengers is 0")

    def test_origin_destination_alphabetic_validation(self):
        """Test that origin and destination must contain only alphabetic characters and spaces."""
        form = RideSearchForm(data={**self.valid_data, 'origin': 'Leiden123'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when origin contains numbers")
        self.assertIn('origin', form.errors, msg="origin field should have errors when containing numbers")

        form = RideSearchForm(data={**self.valid_data, 'destination': 'Delft!@#'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when destination contains special characters")
        self.assertIn('destination', form.errors, msg="destination field should have errors when containing special characters")

    def test_search_form_date_in_past(self):
        """Test that RideSearchForm is invalid when date is in the past."""
        past_date = '2020-01-01'
        data = {**self.valid_data, 'date': past_date}
        form = RideSearchForm(data=data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when date is in the past")
        self.assertIn('date', form.errors, msg="date field should have errors when in the past")

class TestRideForm(TestCase):

    def setUp(self):
        """Set up valid and invalid data for testing RideForm."""
        self.valid_data = {
            'origin': 'Amsterdam',
            'destination': 'Rotterdam',
            'date': '2099-01-01T10:00',
            'seats_available': 2,
            'pickup_notes': 'Near the station',
            'status': '1'
        }
        self.invalid_data = {
            'origin': 'A',  # Too short
            'destination': '',
            'date': '',
            'seats_available': 0,  # Too low
            'pickup_notes': '',
            'status': 'invalid'
        }

    def test_origin_min_length_validation(self):
        """ Test that origin field must be at least 3 characters long """
        form = RideForm(data={**self.invalid_data, 'origin': 'A'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when origin is less than 3 characters")
        self.assertIn('origin', form.errors, msg="origin field should have errors when too short")

    def test_destination_min_length_validation(self):
        """ Test that destination field must be at least 3 characters long """
        form = RideForm(data={**self.invalid_data, 'destination': 'B'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when destination is less than 3 characters")
        self.assertIn('destination', form.errors, msg="destination field should have errors when too short")

    def test_origin_destination_alphabetic_validation(self):
        """Test that origin and destination must contain only alphabetic characters and spaces."""
        form = RideForm(data={**self.valid_data, 'origin': 'Amsterdam123'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when origin contains numbers")
        self.assertIn('origin', form.errors, msg="origin field should have errors when containing numbers")

        form = RideForm(data={**self.valid_data, 'destination': 'Rotterdam!@#'})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when destination contains special characters")
        self.assertIn('destination', form.errors, msg="destination field should have errors when containing special characters")

    def test_date_required_validation(self):
        """ Test that date field is required """
        form = RideForm(data={**self.invalid_data, 'date': ''})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when date is missing")
        self.assertIn('date', form.errors, msg="date field should have errors when missing")

    def test_ride_form_date_in_past(self):
        """Test that RideForm is invalid when date is in the past."""
        past_date = '2020-01-01T10:00'
        data = {**self.valid_data, 'date': past_date}
        form = RideForm(data=data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when date is in the past")
        self.assertIn('date', form.errors, msg="date field should have errors when in the past")

    def test_seats_available_min_max_validation(self):
        """ Test that seats_available field must be between 1 and 4 """
        form = RideForm(data={**self.invalid_data, 'seats_available': 0})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when seats_available is less than 1")
        self.assertIn('seats_available', form.errors, msg="seats_available field should have errors when less than 1")

        form = RideForm(data={**self.invalid_data, 'seats_available': 5})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when seats_available is greater than 4")
        self.assertIn('seats_available', form.errors, msg="seats_available field should have errors when greater than 4")

    def test_form_valid_data(self):
        """ Test that form is valid with correct data """
        form = RideForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), msg="Form should be valid with correct data")

    def test_form_invalid_data(self):
        """ Test that form is invalid with incorrect data """
        form = RideForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid with incorrect data")

    def test_origin_whitespace_only(self):
        """Test that origin field with only whitespace is invalid."""
        form = RideForm(data={**self.valid_data, 'origin': '   '})
        self.assertFalse(form.is_valid(), msg="Form should be invalid when origin is only whitespace")
        self.assertIn('origin', form.errors, msg="origin field should have errors when only whitespace")
        
    def test_max_seats_parameter_limits_choices(self):
        """Test that max_seats parameter limits seats_requested choices."""
        form = RideRequestForm(max_seats=2)
        choices = [choice[0] for choice in form.fields['seats_requested'].choices]
        self.assertEqual(choices, ['1', '2'], msg="Choices should be limited to ['1', '2'] when max_seats=2")

class TestRideRequestEditForm(TestCase):

    def setUp(self):
        """Set up valid and invalid data for testing RideRequestEditForm."""
        self.valid_data = {'seats_requested': 2}
        self.invalid_data = {'seats_requested': 5}

    def test_seats_requested_choices(self):
        """Test that seats_requested field only accepts valid choices."""
        form = RideRequestEditForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid when seats_requested is out of range")
        self.assertIn('seats_requested', form.errors, msg="seats_requested field should have errors when invalid")

    def test_edit_form_valid_data(self):
        """Test that form is valid with correct seats_requested value."""
        form = RideRequestEditForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), msg="Form should be valid with correct data")

    def test_edit_form_invalid_data(self):
        """Test that form is invalid with incorrect seats_requested value."""
        form = RideRequestEditForm(data=self.invalid_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid with incorrect data")
        self.assertIn('seats_requested', form.errors, msg="seats_requested field should have errors when invalid")