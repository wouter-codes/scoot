from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Rides, RideRequest


class SearchRidesViewTest(TestCase):
    """
    Test suite for the SearchRidesView.
    """
    def setUp(self):
        """Create a test user and a test ride for SearchRidesView tests."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.client = Client()

    def test_search_rides_get(self):
        """Test GET request to search_rides returns expected response."""
        response = self.client.get(reverse('search_rides'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/search_rides.html')
        self.assertContains(response, 'Find Your Ride')

    def test_search_rides_post(self):
        """Test POST request to search_rides returns expected response."""
        response = self.client.post(reverse('search_rides'), {
            'origin': 'Amsterdam',
            'destination': 'Rotterdam',
            'date': '2099-01-01',
            'min_passengers': 1,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amsterdam → Rotterdam')
        self.assertContains(response, '<strong>Seats:</strong> 2')

    def test_search_rides_draft(self):
        """Test that draft rides are not shown in search results."""
        Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Utrecht',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Draft ride',
            status='0',
        )
        response = self.client.get(reverse('search_rides'))
        self.assertNotContains(response, 'Draft ride')


class MyRidesViewTest(TestCase):
    def setUp(self):
        """Create a test user and a test ride for MyRidesView tests."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.client = Client()

    def test_my_rides_authenticated(self):
        """Test authenticated user can access my_rides view and see rides."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('my_rides'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/my_rides.html')

    def test_my_rides_unauthenticated(self):
        """Test unauthenticated user is redirected from my_rides view."""
        response = self.client.get(reverse('my_rides'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(
            response, f"{reverse('account_signup')}?next={reverse('my_rides')}"
        )


class RideDetailViewTest(TestCase):
    """
    Test suite for the RideDetailView. This suite tests that
    the ride detail view displays the correct information about
    a ride and its associated ride request.
    """
    def setUp(self):
        """
        Create a test user, a test ride, and a test ride request
        for RideDetailView tests."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            ride=self.ride,
            passenger=self.user,
            seats_requested=1,
            status='0',
        )
        self.client = Client()

    def test_ride_detail_view(self):
        """Test that the ride detail view displays the correct information."""
        response = self.client.get(reverse('ride_detail', args=[self.ride.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/ride_detail.html')
        self.assertContains(response, 'Amsterdam → Rotterdam')
        self.assertContains(response, 'Available Seats')
        self.assertContains(response, 'Near the station')


class RequestRideViewTest(TestCase):
    """
    Test suite for the RequestRideView. This suite tests
    both GET and POST requests to the request_ride view,
    ensuring that the correct templates are used and that
    the ride request functionality works as expected.
    """
    def setUp(self):
        """Create a test user and a test ride for RequestRideView tests."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.client = Client()

    def test_request_ride_get(self):
        """
        Test that the request_ride view returns a
        200 status codefor GET requests.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(
            reverse('request_ride', args=[self.ride.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/request_ride.html')

    def test_request_ride_post_valid(self):
        """
        Test that a valid POST request to request_ride
        creates a new ride request.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('request_ride', args=[self.ride.id]),
            {
                'seats_requested': 1,
            }
        )
        # Redirect after successful request
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            RideRequest.objects.filter(
                ride=self.ride,
                passenger=self.user
            ).exists(),
            msg=(
                "RideRequest should not be "
                "created with invalid POST data"
            )
        )

    def test_request_ride_post_invalid(self):
        """
        Test that an invalid POST request to request_ride
        does not create a new ride request.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('request_ride', args=[self.ride.id]),
            {'seats_requested': 0, }  # Invalid number of seats
        )
        # Form should be re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            RideRequest.objects.filter(
                ride=self.ride,
                passenger=self.user
            ).exists(),
            msg=(
                "RideRequest should not be "
                "created with invalid POST data"
            )
        )

    def test_request_ride_no_seats(self):
        """
        Test that a POST request to request_ride does not create
        a new ride request when there are no seats available.
        """
        self.ride.seats_available = 0
        self.ride.save()
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('request_ride', args=[self.ride.id]),
            {'seats_requested': 1, }
        )
        # Form should be re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            RideRequest.objects.filter(
                ride=self.ride,
                passenger=self.user
            ).exists(),
            msg=(
                "RideRequest should not be created "
                "when no seats are available"
            )
        )

    def test_request_ride_multiple_users(self):
        """Test that a passenger can request a ride from another driver."""
        passenger = User.objects.create_user(
            username='passenger', password='passpass'
        )
        self.client.login(username='passenger', password='passpass')
        response = self.client.post(
            reverse('request_ride', args=[self.ride.id]),
            {'seats_requested': 1, }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            RideRequest.objects.filter(
                ride=self.ride,
                passenger=passenger
            ).exists()
        )

    def test_request_ride_overbooking(self):
        """Test that requesting more seats than available fails."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('request_ride', args=[self.ride.id]),
            {'seats_requested': 5}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            RideRequest.objects.filter(
                ride=self.ride,
                passenger=self.user,
                seats_requested=5
            ).exists()
        )


class RideRequestConfirmationViewTest(TestCase):
    """
    Test suite for the RideRequestConfirmationView.
    This suite tests that the ride request confirmation view displays
    the correct information about a ride request and allows users to
    confirm their ride requests.
    """
    def setUp(self):
        """
        Create a test user, a test ride,
        and a test ride request for
        RideRequestConfirmationView tests.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            ride=self.ride,
            passenger=self.user,
            seats_requested=1,
            status='0',
        )
        self.client = Client()

    def test_ride_request_confirmation_view(self):
        """
        Test that the ride request confirmation view
        displays the correct information.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(
            reverse('ride_request_confirmation', args=[self.ride_request.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'rides/ride_request_confirmation.html'
        )
        self.assertContains(response, 'Request Sent!')
        self.assertContains(response, 'Amsterdam → Rotterdam')
        self.assertContains(
            response,
            '<strong>Seats Requested:</strong> 1'
        )
        self.assertContains(response, 'Near the station')


class CreateRideViewTest(TestCase):
    """
    Test suite for the CreateRideView.
    This suite tests both GET and POST requests to the create_ride view,
    ensuring that the correct templates are used and that the ride creation
    functionality works as expected.
    """
    def setUp(self):
        """Create a test user for CreateRideView tests."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client = Client()

    def test_create_ride_get(self):
        """
        Test that the create_ride view returns
        a 200 status code for GET requests.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('create_ride'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/create_ride.html')

    def test_create_ride_post_publish(self):
        """
        Test that the create_ride view correctly
        creates a published ride.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('create_ride'), {
                'origin': 'Amsterdam',
                'destination': 'Rotterdam',
                'date': '2099-01-01 10:00:00',
                'seats_available': 2,
                'pickup_notes': 'Near the station',
                'status': 1,
            }
        )
        self.assertEqual(
            response.status_code,
            302  # Should redirect to the ride detail page
        )
        self.assertTrue(
            Rides.objects.filter(
                origin='Amsterdam',
                destination='Rotterdam'
            ).exists()
        )

    def test_create_ride_post_draft(self):
        """Test that the create_ride view correctly creates a draft ride."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('create_ride'), {
            'origin': 'Amsterdam',
            'destination': 'Rotterdam',
            'date': '2099-01-01 10:00:00',
            'seats_available': 2,
            'pickup_notes': 'Near the station',
            'status': 0,
        })
        self.assertEqual(
            response.status_code,
            302  # Should redirect to the my rides page
        )
        self.assertTrue(
            Rides.objects.filter(
                origin='Amsterdam',
                destination='Rotterdam',
                status='0'
            ).exists()
        )

    def test_create_ride_post_invalid(self):
        """
        Test that the create_ride view does not
        create a ride with invalid data.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('create_ride'), {
            'origin': '',
            'destination': '',
            'date': '',
            'seats_available': '',
            'pickup_notes': '',
            'status': 1,
        })
        self.assertEqual(
            response.status_code,
            200  # Form should be re-rendered with errors
        )
        self.assertFalse(
            Rides.objects.filter(
                origin='',
                destination=''
            ).exists(),
            msg=(
                "Ride should not be created "
                "with invalid POST data"
            )
        )

    def test_create_ride_unauthenticated(self):
        """
        Test that an unauthenticated user cannot
        access the create_ride view.
        """
        response = self.client.get(reverse('create_ride'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(
            response,
            (
                f"{reverse('account_signup')}?next="
                f"{reverse('create_ride')}"
            )
        )


class EditRideViewTest(TestCase):
    """
    Test suite for the EditRideView.
    This suite tests both GET and POST requests to the edit_ride view,
    ensuring that the correct templates are used and that the ride editing
    functionality works as expected.
    """
    def setUp(self):
        """Create a test user and a test ride for EditRideView tests."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.client = Client()

    def test_edit_ride_get(self):
        """
        Test that the edit_ride view returns
        a 200 status code for GET requests.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('edit_ride', args=[self.ride.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/edit_ride.html')

    def test_edit_ride_post(self):
        """Test that a POST request to edit_ride updates the ride."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('edit_ride', args=[self.ride.id]),
            {
                'origin': 'Amsterdam',
                'destination': 'The Hague',
                'date': '2099-01-01 10:00:00',
                'seats_available': 2,
                'pickup_notes': 'Near the station',
                'status': '1',
                'publish': '1',
            }
        )
        self.assertIn(
            response.status_code,
            [200, 302]
        )  # Accept both redirect and success
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.destination, 'The Hague')


class DeleteRideViewTest(TestCase):
    """
    Test suite for the DeleteRideView.
    This suite tests that a ride can be successfully deleted and that
    the user is redirected to the appropriate page after deletion.
    """
    def setUp(self):
        """Create a test user and a test ride for DeleteRideView tests."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.client = Client()

    def test_delete_ride_post(self):
        """Test that a POST request to delete_ride deletes the ride."""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('delete_ride', args=[self.ride.id])
        )
        self.assertEqual(
            response.status_code,
            302  # Should redirect to the my rides page
        )
        self.assertFalse(
            Rides.objects.filter(
                id=self.ride.id
            ).exists(),
            msg=(
                "Ride should be deleted "
                "after POST request"
            )
        )


class MyRideRequestsViewTest(TestCase):
    """
    Test suite for the MyRideRequestsView.
    This suite tests that an authenticated user can access the
    my_ride_requests view and see their ride requests, while an
    unauthenticated user is redirected to the login page.
    """
    def setUp(self):
        """
        Create a test user and a test ride request
        for MyRideRequestsView tests.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            passenger=self.user,
            ride=self.ride,
            status='pending'
        )
        self.client = Client()

    def test_my_ride_requests_authenticated(self):
        """
        Test that an authenticated user can access
        the my_ride_requests view.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('my_ride_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/my_ride_requests.html')

    def test_my_ride_requests_unauthenticated(self):
        """
        Test that an unauthenticated user is redirected
        when trying to access the my_ride_requests view.
        """
        response = self.client.get(reverse('my_ride_requests'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertRedirects(
            response,
            (
                f"{reverse('account_signup')}?next="
                f"{reverse('my_ride_requests')}"
            )
        )


class EditRideRequestViewTest(TestCase):
    """
    Test suite for the EditRideRequestView.
    This suite tests both GET and POST requests to the edit_ride_request view,
    ensuring that the correct templates are used and that the
    ride request editing functionality works as expected.
    """
    def setUp(self):
        """
        Create a test user and a test ride request
        for EditRideRequestView tests.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            passenger=self.user,
            ride=self.ride,
            status='pending'
        )
        self.client = Client()

    def test_edit_ride_request_get(self):
        """
        Test that a GET request to edit_ride_request
        returns the correct template.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(
            reverse('edit_ride_request', args=[self.ride_request.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rides/edit_ride_request.html')

    def test_edit_ride_request_post(self):
        """
        Test that a POST request to edit_ride_request
        updates the ride request.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('edit_ride_request', args=[self.ride_request.id]),
            {'seats_requested': 2, }
        )
        # Should redirect to the my ride requests page
        self.assertEqual(response.status_code, 302)
        self.ride_request.refresh_from_db()
        self.assertEqual(
            self.ride_request.seats_requested,
            2
        )


class CancelRideRequestViewTest(TestCase):
    """
    Test suite for the CancelRideRequestView.
    This suite tests that a ride request can be successfully canceled
    and that the user is redirected to the appropriate page after cancellation.
    """
    def setUp(self):
        """
        Create a test user and a test ride request for
        CancelRideRequestView tests.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
            )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            passenger=self.user,
            ride=self.ride,
            status='0'
        )
        self.client = Client()

    def test_cancel_ride_request_post(self):
        """
        Test that a POST request to cancel_ride_request
        cancels the ride request.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('cancel_ride_request', args=[self.ride_request.id])
        )
        # Should redirect to the my ride requests page
        self.assertEqual(response.status_code, 302)
        # If RideRequest was pending, it is deleted after cancel
        exists = RideRequest.objects.filter(id=self.ride_request.id).exists()
        if exists:
            self.ride_request.refresh_from_db()
            self.assertEqual(
                self.ride_request.status,
                '3'
            )
        else:
            # Pending request should be deleted
            self.assertFalse(exists)

    def test_cancel_already_finalized_request(self):
        """
        Test that cancelling an already cancelled request
        does not change its status.
        """
        self.ride_request.status = 3
        self.ride_request.save()
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('cancel_ride_request', args=[self.ride_request.id])
        )
        self.ride_request.refresh_from_db()
        self.assertEqual(
            self.ride_request.status,
            '3'
        )
        self.assertIn(response.status_code, [200, 302])


class ApproveRideRequestViewTest(TestCase):
    """
    Test suite for the ApproveRideRequestView.
    This suite tests that a ride request can be successfully approved
    and that the user is redirected to the appropriate page after
    approval.
    """
    def setUp(self):
        """
        Create a test user and a test ride request for
        ApproveRideRequestView tests.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            passenger=self.user,
            ride=self.ride,
            status='0'
        )
        self.client = Client()

    def test_approve_ride_request_post(self):
        """
        Test that a POST request to approve_ride_request
        approves the ride request.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('approve_ride_request', args=[self.ride_request.id])
        )
        # Should redirect to the my ride requests page
        self.assertEqual(response.status_code, 302)
        self.ride_request.refresh_from_db()
        self.assertEqual(
            self.ride_request.status,
            '1'
        )
        self.assertIn(response.status_code, [200, 302])

    def test_approve_already_finalized_request(self):
        """
        Test that approving an already approved request
        does not change its status.
        """
        self.ride_request.status = 1
        self.ride_request.save()
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('approve_ride_request', args=[self.ride_request.id])
        )
        self.ride_request.refresh_from_db()
        self.assertEqual(
            self.ride_request.status,
            '1'
        )
        self.assertIn(response.status_code, [200, 302])


class RejectRideRequestViewTest(TestCase):
    """
    Test suite for the RejectRideRequestView.
    This suite tests that a ride request can be successfully rejected
    and that the user is redirected to the appropriate page after rejection.
    """
    def setUp(self):
        """
        Create a test user and a test ride request for
        RejectRideRequestView tests.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
            )
        self.ride = Rides.objects.create(
            driver=self.user,
            origin='Amsterdam',
            destination='Rotterdam',
            date='2099-01-01 10:00:00',
            seats_available=2,
            pickup_notes='Near the station',
            status='1',
        )
        self.ride_request = RideRequest.objects.create(
            passenger=self.user,
            ride=self.ride,
            status='0'
        )
        self.client = Client()

    def test_reject_ride_request_post(self):
        """
        Test that a POST request to reject_ride_request
        rejects the ride request.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('reject_ride_request', args=[self.ride_request.id])
        )
        # Should redirect to the my ride requests page
        self.ride_request.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.ride_request.status,
            '2'
        )
        self.assertIn(response.status_code, [200, 302])

    def test_reject_already_finalized_request(self):
        """
        Test that rejecting an already rejected request
        does not change its status.
        """
        self.ride_request.status = 2
        self.ride_request.save()
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('reject_ride_request', args=[self.ride_request.id])
        )
        self.ride_request.refresh_from_db()
        self.assertEqual(
            self.ride_request.status,
            '2'
        )
        self.assertIn(response.status_code, [200, 302])


class AboutViewTest(TestCase):
    """
    Test suite for the AboutView.
    This suite tests that the about view returns the correct template
    and contains the expected content.
    """
    def test_about_view(self):
        """
        Test that the about view returns the correct template
        and contains the expected content.
        """
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')
        self.assertContains(response, 'About Scoot')
