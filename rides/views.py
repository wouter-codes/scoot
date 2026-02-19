from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import mark_safe
from django.urls import reverse
from .models import Rides, RideRequest, UserProfile
from .forms import RideSearchForm

def index(request):
    """Render the home page with ride search form"""
    form = RideSearchForm(request.GET or None)
    rides = Rides.objects.filter(
        date__gt=timezone.now(),
        seats_available__gt=0,
        status='1'  # Only published rides
    ).order_by('date')
    
    # Apply filters if form is valid
    if form.is_valid():
        origin = form.cleaned_data.get('origin')
        destination = form.cleaned_data.get('destination')
        date = form.cleaned_data.get('date')
        min_passengers = form.cleaned_data.get('min_passengers')
        
        if origin:
            rides = rides.filter(origin__icontains=origin)
        if destination:
            rides = rides.filter(destination__icontains=destination)
        if date:
            rides = rides.filter(date__date=date)
        if min_passengers:
            rides = rides.filter(seats_available__gte=min_passengers)
    
    context = {
        'form': form,
        'rides': rides
    }
    return render(request, 'rides/index.html', context)


def book_ride(request, ride_id):
    """
    Handle ride booking. Users select number of seats and confirm.
    Redirects to signup if not logged in.
    """
    if not request.user.is_authenticated:
        login_url = reverse('account_login')
        message = f'You need to be logged in to book a ride. Sign up or <a href="{login_url}" class="link">log in</a> to continue.'
        messages.warning(request, mark_safe(message))
        return redirect('account_signup')
    
    ride = get_object_or_404(Rides, id=ride_id)
    
    # Check if ride has available seats
    if ride.seats_available <= 0:
        messages.error(request, 'This ride has no available seats.')
        return redirect('index')
    
    if request.method == 'POST':
        seats_requested = int(request.POST.get('seats_requested', 1))
        
        # Validate seats requested
        if seats_requested < 1 or seats_requested > ride.seats_available:
            context = {
                'ride': ride,
                'error': f'Please select between 1 and {ride.seats_available} seats'
            }
            return render(request, 'rides/book_ride.html', context)
        
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
    return render(request, 'rides/book_ride.html', context)


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