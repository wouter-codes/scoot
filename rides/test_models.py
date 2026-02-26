from datetime import datetime
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from rides.forms import RideSearchForm
from .models import Rides, RideRequest, validate_future_date

class RidesModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create a test ride
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date=make_aware(datetime(2099, 1, 1, 10, 0)),
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )

    def test_ride_str_method(self):
        # Test the string representation of the Rides model
        expected_str = f"{self.ride.origin} to {self.ride.destination} on {self.ride.date.strftime('%Y-%m-%d %H:%M')} - {self.ride.seats_available} seats"
        self.assertEqual(str(self.ride), expected_str)

    def test_ride_clean_method(self):
        # Test that the clean method raises a ValidationError when origin and destination are the same
        self.ride.destination = self.ride.origin
        with self.assertRaises(ValidationError):
            self.ride.clean()

    def test_ride_meta_ordering(self):
        # Test that the default ordering is descending by created_on
        self.assertEqual(Rides._meta.ordering, ['-created_on'])

    def test_default_values(self):
        # Test that default values are set correctly when not provided
        default_value_test_ride = Rides.objects.create(
            driver=self.user,
            origin=self.ride.origin,
            destination=self.ride.destination,
            date=self.ride.date,
            pickup_notes=self.ride.pickup_notes,
        )
        self.assertEqual(default_value_test_ride.seats_available, 1)
        self.assertEqual(default_value_test_ride.status, '0')

    def test_pickup_notes_required_or_blank(self):
        # Test if pickup_notes is required or can be blank
        ride_with_blank_notes = Rides.objects.create(
            driver=self.user,
            origin=self.ride.origin,
            destination=self.ride.destination,
            date=self.ride.date,
            seats_available=2,
            pickup_notes='',
        )
        self.assertEqual(ride_with_blank_notes.pickup_notes, '')

    def test_created_on_and_updated_on_auto_fields(self):
        # Test that created_on and updated_on are set automatically
        self.assertIsNotNone(self.ride.created_on)
        self.assertIsNotNone(self.ride.updated_on)

    # Tests for the validate_future_date function
    def test_validate_future_date_with_past_date(self):
        # Test that a past date raises a ValidationError
        past_date = make_aware(datetime(2000, 1, 1, 10, 0))
        with self.assertRaises(ValidationError):
            validate_future_date(past_date)

class RideRequestModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser2', password='testpass')
        # Create a test ride
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Utrecht',
            destination='Eindhoven',
            date=make_aware(datetime(2099, 1, 2, 12, 0)),
            seats_available=3,
            pickup_notes='Main entrance',
            status='1',
        )
        # Create a test ride request
        self.ride_request = RideRequest.objects.create(
            passenger=self.user,
            ride=self.ride,
            seats_requested=1,
            status='0',
        )

    def test_ride_request_str_method(self):
        # Test the string representation of the RideRequest model
        expected_str = f"Ride ID:{self.ride.id} | RideRequest by {self.user.username} for ride from {self.ride.origin} to {self.ride.destination} - Status: {self.ride_request.get_status_display()}"
        self.assertEqual(str(self.ride_request), expected_str)

    def test_ride_request_unique_together(self):
        # Test that creating a duplicate ride request for the same passenger and ride raises an error
        with self.assertRaises(IntegrityError):
            RideRequest.objects.create(
                passenger=self.user,
                ride=self.ride,
                seats_requested=1,
                status='0',
            )

    def test_ride_request_status_choices(self):
        # Test that the status field only accepts valid choices
        with self.assertRaises(ValidationError):
            self.ride_request.status = 'invalid_status'
            self.ride_request.full_clean()  # This will trigger validation

    def test_ride_request_meta_ordering(self):
        # Test that the default ordering is descending by created_on
        self.assertEqual(RideRequest._meta.ordering, ['-created_on'])

    def test_default_values(self):
        # Test that default values are set correctly when not provided
        new_ride = Rides.objects.create(
            driver=self.user,
            origin='Somewhere',
            destination='Elsewhere',
            date=make_aware(datetime(2099, 1, 3, 15, 0)),
            seats_available=2,
            pickup_notes='Test',
            status='1',
        )
        default_value_test_request = RideRequest.objects.create(
            passenger=self.user,
            ride=new_ride,
            )
        self.assertEqual(default_value_test_request.seats_requested, 1)
        self.assertEqual(default_value_test_request.status, '0')

    def test_seats_requested_min_max_validation(self):
        # Test that seats_requested enforces min and max value validation
        with self.assertRaises(ValidationError):
            self.ride_request.seats_requested = 0
            self.ride_request.full_clean()  # This will trigger validation
        with self.assertRaises(ValidationError):
            self.ride_request.seats_requested = 5
            self.ride_request.full_clean()  # This will trigger validation

    def test_created_on_and_updated_on_auto_fields(self):
        # Test that created_on and updated_on are set automatically
        self.assertIsNotNone(self.ride_request.created_on)
        self.assertIsNotNone(self.ride_request.updated_on)

class RidesQuerySetTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='queryuser', password='testpass')
        # Create multiple rides for queryset filtering
        self.ride1 = Rides.objects.create(
            driver=self.user,
            origin='Leiden',
            destination='Delft',
            date=make_aware(datetime(2099, 1, 3, 10, 0)),
            seats_available=1,
            pickup_notes='Bus stop',
            status='1',
        )
        self.ride2 = Rides.objects.create(
            driver=self.user,
            origin='Leiden',
            destination='Amsterdam',
            date=make_aware(datetime(2099, 1, 4, 14, 0)),
            seats_available=4,
            pickup_notes='Central square',
            status='1',
        )

    def test_apply_search_filters_with_valid_form(self):
        # Create a valid form with search criteria
        form_data = {
            'origin': 'Leiden',
            'destination': 'Delft',
            'date': '2099-01-03',
            'min_passengers': 1,
        }
        form = RideSearchForm(data=form_data)
        queryset = Rides.objects.all().apply_search_filters(form)
        self.assertIn(self.ride1, queryset)
        self.assertNotIn(self.ride2, queryset)

    def test_apply_search_filters_with_invalid_form(self):
        # Create an invalid form (e.g., missing required fields)
        form_data = {
            'origin': '',
            'destination': '',
            'date': '',
            'min_passengers': '',
        }
        form = RideSearchForm(data=form_data)
        queryset = Rides.objects.all().apply_search_filters(form)
        # Should return all rides since the form is invalid
        self.assertIn(self.ride1, queryset)
        self.assertIn(self.ride2, queryset)

    def test_apply_search_filters_with_partial_filters(self):
        # Create a form with only origin filter
        form_data = {
            'origin': 'Leiden',
            'destination': '',
            'date': '',
            'min_passengers': '',
        }
        form = RideSearchForm(data=form_data)
        queryset = Rides.objects.all().apply_search_filters(form)
        self.assertIn(self.ride1, queryset)
        self.assertIn(self.ride2, queryset)