from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.utils import timezone
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