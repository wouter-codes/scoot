from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils.html import mark_safe
from django.urls import reverse

from .models import Rides, RideRequest
from .forms import RideSearchForm, RideForm, RideRequestForm, RideRequestEditForm

def homepage(request):
    """
    Show index.html for unauthenticated users, search_rides.html for authenticated users.
    """
    form = RideSearchForm(request.GET or None)
    if not request.user.is_authenticated:
        rides = Rides.objects.filter(
            date__gt=timezone.now(),
            seats_available__gt=0,
            status='1'
        )
        rides = rides.apply_search_filters(form)
        user_request_ids = set()
        rides = rides.order_by('date')
        context = {
            'form': form,
            'rides': rides,
            'user_request_ids': user_request_ids
        }
        return render(request, 'rides/index.html', context)
    else:
        return search_rides(request)

def search_rides(request):
    """
    Display the home page with the ride search form and filtered ride results.
    Applies search filters, excludes rides created or already requested by the user,
    and orders results by date.
    Only published and available rides are shown.
    """
    form = RideSearchForm(request.GET or None)

    # Start with all published, available rides
    rides = Rides.objects.filter(
        date__gt=timezone.now(),
        seats_available__gt=0,
        status='1'  # Only published rides
    )

    # Apply search filters from form (must be called on manager)
    rides = rides.apply_search_filters(form)

    # Exclude rides created by the logged-in user and rides already requested by the user
    if request.user.is_authenticated:
        # Get ride IDs the user has already requested
        user_requests = RideRequest.objects.filter(
            passenger=request.user
        ).values_list('ride_id', flat=True)
        user_request_ids = set(user_requests)
        rides = rides.exclude(driver=request.user).exclude(id__in=user_request_ids)
    else:
        user_request_ids = set()

    # Order by date
    rides = rides.order_by('date')

    context = {
        'form': form,
        'rides': rides,
        'user_request_ids': user_request_ids
    }
    return render(request, 'rides/search_rides.html', context)


@login_required(login_url='account_signup')
def my_rides(request):
    """Display all rides created by the logged-in user."""
    all_rides = Rides.objects.filter(driver=request.user).order_by('-date')
    all_rides = all_rides.annotate(request_count=Count('ride_requests', filter=Q(ride_requests__status='0')))

    published_rides = [r for r in all_rides if r.status == '1']
    draft_rides = [r for r in all_rides if r.status == '0']
    voided_rides = [r for r in all_rides if r.status not in ['0', '1']]

    return render(request, 'rides/my_rides.html', {
        'published_rides': published_rides,
        'draft_rides': draft_rides,
        'voided_rides': voided_rides,
    })


def ride_detail(request, ride_id):
    """
    Display full details for a single ride, including ride info and ride requests.
    If the user is the driver, show all requests for this ride. If the user is a passenger,
    show their own request if it exists. Indicates if any requests have been accepted.
    """
    ride = get_object_or_404(Rides, id=ride_id)
    ride_request = None
    ride_requests = None
    if request.user.is_authenticated:
        ride_request = RideRequest.objects.filter(ride=ride, passenger=request.user).first()
        # If user is driver, show all requests for this ride
        if request.user == ride.driver:
            ride_requests = RideRequest.objects.filter(ride=ride)
    return render(request, 'rides/ride_detail.html', {
        'ride': ride,
        'ride_request': ride_request,
        'ride_requests': ride_requests,
    })


def request_ride(request, ride_id):
    """
    Handle ride request submission for a specific ride.
    Users select number of seats and confirm. Redirects to signup if not logged in.
    Validates seat availability and creates a pending ride request.
    """
    if not request.user.is_authenticated:
        login_url = reverse('account_login')
        message = f'You need to be logged in to request a ride. Sign up or <a href="{login_url}" class="link">log in</a> to continue.'
        messages.warning(request, mark_safe(message))
        return redirect('account_signup')

    ride = get_object_or_404(Rides, id=ride_id)

    # Check if ride has available seats
    if ride.seats_available <= 0:
        messages.error(request, 'This ride has no available seats.')
        return redirect('search_rides')

    if request.method == 'POST':
        form = RideRequestForm(request.POST, max_seats=ride.seats_available)
        if form.is_valid():
            ride_request = form.save(commit=False)
            ride_request.passenger = request.user
            ride_request.ride = ride
            ride_request.status = '0'  # Pending status
            ride_request.save()
            return redirect('ride_request_confirmation', request_id=ride_request.id)
        else:
            context = {'ride': ride, 'form': form}
            return render(request, 'rides/request_ride.html', context)
    else:
        form = RideRequestForm(max_seats=ride.seats_available)
    context = {'ride': ride, 'form': form}
    return render(request, 'rides/request_ride.html', context)


@login_required(login_url='account_signup')
def ride_request_confirmation(request, request_id):
    """
    Display booking confirmation page after a successful ride request submission.
    Only accessible to the passenger who made the request.
    """
    ride_request = get_object_or_404(RideRequest, id=request_id, passenger=request.user)

    context = {
        'ride_request': ride_request,
    }
    return render(request, 'rides/ride_request_confirmation.html', context)


@login_required(login_url='account_signup')
def create_ride(request):
    """
    Allow logged-in users to create a new ride listing.
    Handles both publishing and saving as draft, depending on which button is pressed.
    """
    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            # Check which button was pressed
            publish_value = request.POST.get('publish', '')
            if publish_value == '1':
                ride.status = '1'  # Published
                ride.save()
                messages.success(request, 'Your ride has been published successfully!')
            elif publish_value == '0':
                ride.status = '0'  # Draft
                ride.save()
                messages.info(request, 'Your ride has been saved as a draft.')
            else:
                ride.status = '0'  # Default to draft
                ride.save()
                messages.info(request, 'Your ride has been saved as a draft.')
            return redirect('my_rides')
        else:
            messages.error(request, 'Please correct the errors below to create your ride.')
    else:
        form = RideForm()
    return render(request, 'rides/create_ride.html', {'form': form})


@login_required(login_url='account_signup')
def edit_ride(request, ride_id):
    """
    Allow the ride creator to edit their ride listing.
    Only the driver can edit. Prevents saving as draft if there are ride requests.
    """
    ride = get_object_or_404(Rides, id=ride_id)
    if ride.driver == request.user:
        form = RideForm(request.POST or None, instance=ride)
        if request.method == 'POST':
            if form.is_valid():
                ride = form.save(commit=False)
                if request.POST.get('publish') == '1':
                    ride.status = '1'  # Published
                    ride.save()
                    messages.success(request, 'Ride published successfully!')
                    return redirect('my_rides')
                elif request.POST.get('publish') == '0':
                    if ride.ride_requests.exists():
                        messages.error(request, 'You cannot save this ride as a draft because there are ride requests for it.')
                        return render(request, 'rides/edit_ride.html', {'form': form, 'ride': ride})
                    ride.status = '0'  # Draft
                    ride.save()
                    messages.info(request, 'Ride saved as draft.')
                    return redirect('my_rides')
            else:
                messages.error(request, 'Please correct the errors below to update your ride.')
        return render(request, 'rides/edit_ride.html', {'form': form, 'ride': ride})
    else:
        messages.add_message(request, messages.ERROR, 'You can only edit your own rides!')
        return redirect('my_rides')


@login_required(login_url='account_signup')
def delete_ride(request, ride_id):
    """
    Allow the ride creator to delete their ride listing, or cancel if accepted requests exist.
    If there are accepted requests, cancels the ride and notifies passengers instead of deleting.
    """
    ride = get_object_or_404(Rides, id=ride_id)
    if ride.driver == request.user:
        now = timezone.now()
        if ride.ride_requests.count() == 0 or ride.date < now:
            ride.delete()
            messages.add_message(request, messages.SUCCESS, 'Ride deleted successfully!')
        elif ride.status == '1':  # Published with requests
            ride.status = '2'  # Update to status "Cancelled"
            ride.save()
            # Update all pending and accepted requests to 'Cancelled by driver'
            ride.ride_requests.filter(status__in=['0', '1']).update(status='5')
            messages.add_message(request, messages.WARNING, 'Ride cancelled. Passengers with ride requests have been notified.')
        else:
            messages.add_message(request, messages.ERROR, 'This cancelled ride cannot be deleted because it has ride requests attached and is set in the future.')
    else:
        messages.add_message(request, messages.ERROR, 'You can only delete your own rides!')
    return redirect('my_rides')


@login_required(login_url='account_signup')
def my_ride_requests(request):
    """
    Display all ride requests (bookings) for the logged-in user, grouped by status.
    Shows accepted, pending, and voided (cancelled/rejected) requests.
    """
    all_requests = RideRequest.objects.filter(
        passenger=request.user
    ).select_related('ride').order_by('-ride__date')

    accepted_requests = [r for r in all_requests if r.status == '1']
    pending_requests = [r for r in all_requests if r.status == '0']
    voided_requests = [r for r in all_requests if r.status in ['2', '3', '4', '5']]

    context = {
        'accepted_requests': accepted_requests,
        'pending_requests': pending_requests,
        'voided_requests': voided_requests,
    }
    return render(request, 'rides/my_ride_requests.html', context)


@login_required(login_url='account_signup')
def edit_ride_request(request, request_id):
    """
    Allow passenger to edit their ride request (change seat number).
    Validates seat availability and updates both the ride and the request accordingly.
    """
    ride_request = get_object_or_404(RideRequest, id=request_id, passenger=request.user)
    ride = ride_request.ride
    old_seats = ride_request.seats_requested
    max_allowed = ride.seats_available + old_seats
    if request.method == 'POST':
        form = RideRequestEditForm(request.POST, instance=ride_request, max_seats=max_allowed)
        if form.is_valid():
            new_seats = form.cleaned_data['seats_requested']
            max_allowed = ride.seats_available + old_seats
            if new_seats > max_allowed:
                messages.error(request, f'Only {max_allowed} seats are available to request for this ride.')
                return render(request, 'rides/edit_ride_request.html', {'form': form, 'ride_request': ride_request})
            seat_diff = new_seats - old_seats
            if seat_diff > 0:
                ride.seats_available -= seat_diff
                ride.save()
                form.save()
                messages.success(request, f'Requested seat number updated to {new_seats}.')
            else:
                # If reducing seats, restore seats to ride
                ride.seats_available += abs(seat_diff)
                ride.save()
                form.save()
                messages.success(request, f'Requested seat number updated to {new_seats}.')
            return redirect('my_ride_requests')
    else:
        form = RideRequestEditForm(instance=ride_request, max_seats=max_allowed)
    return render(request, 'rides/edit_ride_request.html', {'form': form, 'ride_request': ride_request})


@login_required(login_url='account_signup')
def cancel_ride_request(request, request_id):
    """
    Allow passenger or driver to cancel a ride request.
    Restores seats if the request was approved. Handles both pending and approved requests.
    Only the passenger or the driver can perform this action.
    """
    ride_request = get_object_or_404(RideRequest, id=request_id)
    ride = ride_request.ride
    # Only allow the passenger or the driver to cancel
    if request.user != ride_request.passenger and request.user != ride.driver:
        messages.error(request, 'You are not authorized to cancel this request.')
        return redirect('ride_detail', ride_id=ride.id)
    if request.method == 'POST':
        # Only allow cancel if pending or approved
        if ride_request.status == '1':
            # Restore seats if previously approved
            ride.seats_available += ride_request.seats_requested
            ride.save()
            # Set status to cancelled by passenger or driver
            if request.user == ride_request.passenger:
                ride_request.status = '3'  # Cancelled by passenger
            else:
                ride_request.status = '5'  # Cancelled by driver
            ride_request.save()
            messages.success(request, 'The approved ride request was cancelled and the seat(s) restored.')
        elif ride_request.status == '0':
            # Pending: just delete, no seat restoration needed
            ride_request.delete()
            messages.success(request, 'The pending ride request was cancelled.')
        else:
            messages.error(request, 'You cannot cancel a declined or already cancelled request.')
        # Redirect to appropriate page
        if request.user == ride.driver:
            return redirect('ride_detail', ride_id=ride.id)
        else:
            return redirect('my_ride_requests')
    # GET fallback
    if request.user == ride.driver:
        return redirect('ride_detail', ride_id=ride.id)
    else:
        return redirect('my_ride_requests')


@login_required(login_url='account_signup')
def approve_ride_request(request, request_id):
    """
    Allow the driver to approve a pending ride request and deduct seats from the ride.
    Only the driver can approve, and only if enough seats are available.
    """
    ride_request = get_object_or_404(RideRequest, id=request_id)
    ride = ride_request.ride
    if request.user != ride.driver:
        messages.error(request, 'You are not authorized to approve this request.')
        return redirect('ride_detail', ride_id=ride.id)
    if ride_request.status != '0':
        messages.error(request, 'Only pending requests can be approved.')
        return redirect('ride_detail', ride_id=ride.id)
    if ride.seats_available < ride_request.seats_requested:
        messages.error(request, f'Not enough seats available to approve this request. Only {ride.seats_available} left.')
        return redirect('ride_detail', ride_id=ride.id)
    # Approve and deduct seats
    ride.seats_available -= ride_request.seats_requested
    ride.save()
    ride_request.status = '1'  # Approved
    ride_request.save()
    messages.success(request, 'Ride request approved and seats reserved.')
    return redirect('ride_detail', ride_id=ride.id)


@login_required(login_url='account_signup')
def reject_ride_request(request, request_id):
    """
    Allow the driver to reject a pending ride request.
    Only the driver can reject, and only if the request is still pending.
    """
    ride_request = get_object_or_404(RideRequest, id=request_id)
    ride = ride_request.ride
    if request.user != ride.driver:
        messages.error(request, 'You are not authorized to reject this request.')
        return redirect('ride_detail', ride_id=ride.id)
    if ride_request.status != '0':
        messages.error(request, 'Only pending requests can be rejected.')
        return redirect('ride_detail', ride_id=ride.id)
    if request.method == 'POST':
        ride_request.status = '2'  # Rejected
        ride_request.save()
        messages.success(request, 'Ride request rejected.')
        return redirect('ride_detail', ride_id=ride.id)
    # If GET, show a confirmation page (optional, not implemented here)
    return redirect('ride_detail', ride_id=ride.id)


def about(request):
    """Render the About page."""
    return render(request, 'about.html')
