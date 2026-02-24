from django.test import TestCase
from .forms import RideRequestForm, RideSearchForm, RideCreateForm, RideEditForm

# Create your tests here.
class TestRideRequestForm(TestCase):

    def test_form_is_valid(self):
        """ Test for all fields"""
        form = RideRequestForm({
            'name': 'Test User',
            'seats_requested': 2
        })
        self.assertTrue(form.is_valid(), msg="Form is not valid")