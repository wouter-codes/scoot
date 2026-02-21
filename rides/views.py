from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import mark_safe
from django.urls import reverse
from .models import Rides, RideRequest, UserProfile
from .forms import RideSearchForm, RideCreateForm

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
        
        # Decrement available seats
        ride.seats_available -= seats_requested
        ride.save()
        
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
            ride.status = '1'  # Published
            ride.save()
            messages.success(request, 'Your ride has been created successfully!')
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
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Ride updated successfully!')
            return redirect('my_rides')
        return render(request, 'rides/edit_ride.html', {'form': form, 'ride': ride})
    else:
        messages.add_message(request, messages.ERROR, 'You can only edit your own rides!')
        return redirect('my_rides')
    
@login_required(login_url='account_signup')
def delete_ride(request, ride_id):
    """Allow ride creator to delete their ride listing."""
    ride = get_object_or_404(Rides, id=ride_id)
    if ride.driver == request.user:
        ride.delete()
        messages.add_message(request, messages.SUCCESS, 'Ride deleted successfully!')
    else:
        messages.add_message(request, messages.ERROR, 'You can only delete your own rides!')
    return redirect('my_rides')

@login_required(login_url='account_signup')
def my_rides(request):
    """Display all rides created by the logged-in user."""
    rides = Rides.objects.filter(driver=request.user).order_by('-date')
    
    return render(request, 'rides/my_rides.html', {'rides': rides})


@login_required(login_url='account_signup')
def my_ride_requests(request):
    """
    Display all ride requests (bookings) for the logged-in user.
    """
    ride_requests = RideRequest.objects.filter(
        passenger=request.user
    ).select_related('ride').order_by('-ride__date')
    
    context = {
        'ride_requests': ride_requests,
    }
    return render(request, 'rides/my_ride_requests.html', context)

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