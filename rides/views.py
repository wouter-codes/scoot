from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils.html import mark_safe
from django.urls import reverse
from .models import Rides, RideRequest, UserProfile
from .forms import RideSearchForm, RideCreateForm, RideRequestEditForm

def search_rides(request):
    """Render the home page with ride search form"""
    form = RideSearchForm(request.GET or None)

    # Start with all published, available rides
    rides = Rides.objects.filter(
        date__gt=timezone.now(),
        seats_available__gt=0,
        status='1'  # Only published rides
    )

    # Apply search filters from form (must be called on manager)
    rides = rides.apply_search_filters(form)

    # Exclude rides created by the logged-in user
    if request.user.is_authenticated:
        rides = rides.exclude(driver=request.user)

    # Order by date
    rides = rides.order_by('date')

    # Add user's existing requests to each ride for template logic
    if request.user.is_authenticated:
        user_requests = RideRequest.objects.filter(
            passenger=request.user,
            ride__in=rides
        ).values_list('ride_id', flat=True)
        user_request_ids = set(user_requests)
    else:
        user_request_ids = set()

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
    """Display full details for a single ride."""
    ride = get_object_or_404(Rides, id=ride_id)
    ride_request = None
    ride_requests = None
    if request.user.is_authenticated:
        ride_request = RideRequest.objects.filter(ride=ride, passenger=request.user).first()
        # If user is driver, show all requests for this ride
        if request.user == ride.driver:
            ride_requests = RideRequest.objects.filter(ride=ride)
    has_accepted_requests = ride.ride_requests.filter(status='1').exists()
    return render(request, 'rides/ride_detail.html', {
        'ride': ride,
        'ride_request': ride_request,
        'ride_requests': ride_requests,
        'has_accepted_requests': has_accepted_requests,
    })

def request_ride(request, ride_id):
    """
    Handle ride request. Users select number of seats and confirm.
    Redirects to signup if not logged in.
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
        seats_requested = int(request.POST.get('seats_requested', 1))
        
        # Validate seats requested
        if seats_requested < 1 or seats_requested > ride.seats_available:
            context = {
                'ride': ride,
                'error': f'Please select between 1 and {ride.seats_available} seats'
            }
            return render(request, 'rides/request_ride.html', context)
        
        # Create the ride request
        ride_request = RideRequest.objects.create(
            passenger=request.user,
            ride=ride,
            seats_requested=seats_requested,
            status='0'  # Pending status
        )
        
        # Do not decrement available seats here; seats will be deducted only when request is approved
        
        # Redirect to confirmation page
        return redirect('ride_request_confirmation', request_id=ride_request.id)
    
    context = {
        'ride': ride,
    }
    return render(request, 'rides/request_ride.html', context)

@login_required(login_url='account_signup')
def ride_request_confirmation(request, request_id):
    """
    Display booking confirmation page after successful booking.
    """
    ride_request = get_object_or_404(RideRequest, id=request_id, passenger=request.user)
    
    context = {
        'ride_request': ride_request,
    }
    return render(request, 'rides/ride_request_confirmation.html', context)

@login_required(login_url='account_signup')
def create_ride(request):
    """Allow logged-in users to create a new ride listing."""
    if request.method == 'POST':
        form = RideCreateForm(request.POST)
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
        form = RideCreateForm()
    
    return render(request, 'rides/create_ride.html', {'form': form})

@login_required(login_url='account_signup')
def edit_ride(request, ride_id):
    """Allow ride creator to edit their ride listing."""
    ride = get_object_or_404(Rides, id=ride_id)
    if ride.driver == request.user:
        form = RideCreateForm(request.POST or None, instance=ride)
        if request.method == 'POST' and form.is_valid():
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
        return render(request, 'rides/edit_ride.html', {'form': form, 'ride': ride})
    else:
        messages.add_message(request, messages.ERROR, 'You can only edit your own rides!')
        return redirect('my_rides')
    
@login_required(login_url='account_signup')
def delete_ride(request, ride_id):
    """Allow ride creator to delete their ride listing, or cancel if accepted requests exist."""
    ride = get_object_or_404(Rides, id=ride_id)
    if ride.driver == request.user:
        # Check for accepted ride requests
        accepted_requests = ride.ride_requests.filter(status='1')
        if accepted_requests.exists():
            # Cancel the ride instead of deleting
            ride.status = '2'  # Cancelled
            ride.save()
            # Update accepted requests to 'Cancelled by driver'
            accepted_requests.update(status='5')
            messages.add_message(request, messages.WARNING, 'Ride cancelled because there were accepted ride requests. Passengers have been notified.')
        else:
            ride.delete()
            messages.add_message(request, messages.SUCCESS, 'Ride deleted successfully!')
    else:
        messages.add_message(request, messages.ERROR, 'You can only delete your own rides!')
    return redirect('my_rides')

@login_required(login_url='account_signup')
def my_ride_requests(request):
    """
    Display all ride requests (bookings) for the logged-in user.
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
    Allow passenger to edit their ride request (increase seat number).
    """
    ride_request = get_object_or_404(RideRequest, id=request_id, passenger=request.user)
    ride = ride_request.ride
    old_seats = ride_request.seats_requested
    if request.method == 'POST':
        form = RideRequestEditForm(request.POST, instance=ride_request)
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
        form = RideRequestEditForm(instance=ride_request)
    return render(request, 'rides/edit_ride_request.html', {'form': form, 'ride_request': ride_request})

@login_required(login_url='account_signup')
def cancel_ride_request(request, request_id):
    """
    Allow passenger or driver to cancel a ride request, restore seats if approved, and show confirmation.
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
    Allow driver to approve a pending ride request and deduct seats.
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
    Allow driver to reject a pending ride request.
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

# Create your views here.
# class PostList(generic.ListView):
#     """
#     Returns all published rides in :model:`rides.Rides`
#     and displays them in a page of six posts. 
#     **Context**

#     ``queryset``
#         All published instances of :model:`rides.Rides`
#     ``paginate_by``
#         Number of posts per page.
        
#     **Template:**

#     :template:`rides/index.html`
#     """
#     queryset = Rides.objects.filter(seats_available__gt=0)
#     template_name = "rides/index.html"
#     paginate_by = 6