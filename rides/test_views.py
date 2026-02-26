from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Rides, RideRequest

class SearchRidesViewTest(TestCase):
    def setUp(self):
        pass

    def test_search_rides_get(self):
        pass

    def test_search_rides_post(self):
        pass

class MyRidesViewTest(TestCase):
    def setUp(self):
        pass

    def test_my_rides_authenticated(self):
        pass

    def test_my_rides_unauthenticated(self):
        pass

class RideDetailViewTest(TestCase):
    def setUp(self):
        pass

    def test_ride_detail_view(self):
        pass

class RequestRideViewTest(TestCase):
    def setUp(self):
        pass

    def test_request_ride_get(self):
        pass

    def test_request_ride_post_valid(self):
        pass

    def test_request_ride_post_invalid(self):
        pass

    def test_request_ride_no_seats(self):
        pass

class RideRequestConfirmationViewTest(TestCase):
    def setUp(self):
        pass

    def test_ride_request_confirmation_view(self):
        pass

class CreateRideViewTest(TestCase):
    def setUp(self):
        pass

    def test_create_ride_get(self):
        pass

    def test_create_ride_post_publish(self):
        pass

    def test_create_ride_post_draft(self):
        pass

    def test_create_ride_post_invalid(self):
        pass

    def test_create_ride_unauthenticated(self):
        pass

class EditRideViewTest(TestCase):
    def setUp(self):
        pass

    def test_edit_ride_get(self):
        pass

    def test_edit_ride_post(self):
        pass

class DeleteRideViewTest(TestCase):
    def setUp(self):
        pass

    def test_delete_ride_post(self):
        pass

class MyRideRequestsViewTest(TestCase):
    def setUp(self):
        pass

    def test_my_ride_requests_authenticated(self):
        pass

    def test_my_ride_requests_unauthenticated(self):
        pass

class EditRideRequestViewTest(TestCase):
    def setUp(self):
        pass

    def test_edit_ride_request_get(self):
        pass

    def test_edit_ride_request_post(self):
        pass

class CancelRideRequestViewTest(TestCase):
    def setUp(self):
        pass

    def test_cancel_ride_request_post(self):
        pass

class ApproveRideRequestViewTest(TestCase):
    def setUp(self):
        pass

    def test_approve_ride_request_post(self):
        pass

class RejectRideRequestViewTest(TestCase):
    def setUp(self):
        pass

    def test_reject_ride_request_post(self):
        pass

class AboutViewTest(TestCase):
    def test_about_view(self):
        pass