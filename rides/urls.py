from django.urls import path # import path, similar to project's urls.py
from . import views # import views.py from the current directory

urlpatterns = [
    path('', views.search_rides, name='search_rides'),
    path('create-ride/', views.create_ride, name='create_ride'),
    path('rides/<int:ride_id>/edit/', views.edit_ride, name='edit_ride'),
    path('rides/<int:ride_id>/delete/', views.delete_ride, name='delete_ride'),
    path('my-rides/', views.my_rides, name='my_rides'),
    path('rides/<int:ride_id>/request/', views.request_ride, name='request_ride'),
    path('booking/<int:request_id>/confirmation/', views.ride_request_confirmation, name='ride_request_confirmation'),
    path('my-ride-requests/', views.my_ride_requests, name='my_ride_requests'),
]