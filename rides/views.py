from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from .models import Rides, RideRequest, UserProfile

def index(request):
    """Render the home page"""
    return render(request, 'rides/index.html')

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