from django.urls import path # import path, similar to project's urls.py
from . import views # import views.py from the current directory

urlpatterns = [
    path('', views.search_rides, name='search_rides'),
    path('rides/<int:ride_id>/book/', views.book_ride, name='book_ride'),
    path('booking/<int:request_id>/confirmation/', views.ride_request_confirmation, name='ride_request_confirmation'),
    path('my-ride-requests/', views.my_ride_requests, name='my_ride_requests'),
]