from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Constants for model field choices
# These tuples define the valid options for seats, ride status, and request status.
SEATS_AVAILABLE = (
    (1, '1 seat'),
    (2, '2 seats'),
    (3, '3 seats'),
    (4, '4 seats'),
)

RIDES_STATUS = (('0', 'Draft'), ('1', 'Published'), ('2', 'Cancelled'))

REQUEST_STATUS = (('0', 'Pending'),
                  ('1', 'Accepted'),
                  ('2', 'Rejected'),
                  ('3', 'Cancelled by passenger'),
                  ('4', 'Completed'),
                  ('5', 'Cancelled by driver'),)

def validate_future_date(value):
    """Ensure ride date is in the future."""
    if value < timezone.now():
        raise ValidationError('Ride date must be in the future.')

class RidesQuerySet(models.QuerySet):
    """Custom QuerySet for Rides."""
    
    def apply_search_filters(self, form):
        """Apply search filters from form to queryset."""
        if not form.is_valid():
            return self
        
        queryset = self
        
        if form.cleaned_data.get('origin'):
            queryset = queryset.filter(origin__icontains=form.cleaned_data['origin'])
        if form.cleaned_data.get('destination'):
            queryset = queryset.filter(destination__icontains=form.cleaned_data['destination'])
        if form.cleaned_data.get('date'):
            queryset = queryset.filter(date__date=form.cleaned_data['date'])
        if form.cleaned_data.get('min_passengers'):
            queryset = queryset.filter(seats_available__gte=form.cleaned_data['min_passengers'])
        
        return queryset

# Create your models here.
class Rides(models.Model):
    """
    Stores a ride entry related to :model:'auth.User'.
    """
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateTimeField(validators=[validate_future_date])
    seats_available = models.IntegerField(choices=SEATS_AVAILABLE, default=1)
    pickup_notes = models.TextField()
    status = models.CharField(max_length=1, choices=RIDES_STATUS, default='0')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    objects = RidesQuerySet.as_manager()
    
    def clean(self):
        """Model-level validation."""
        super().clean()
        if self.origin and self.destination and self.origin.lower() == self.destination.lower():
            raise ValidationError('Origin (pick up) and destination (drop off) must be different.')
        
    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Rides' # ensures the plural form is correct in the admin interface

    def __str__(self):
        date_str = self.date.strftime('%Y-%m-%d %H:%M') if self.date else 'TBD'
        return f"{self.origin} to {self.destination} on {date_str} - {self.seats_available} seats"
    
class RideRequest(models.Model):
    """
    Stores a ride request entry related to :model:'auth.User' and :model:'Rides'.
    """
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_requests_as_passenger')
    ride = models.ForeignKey(Rides, on_delete=models.CASCADE, related_name='ride_requests')
    seats_requested = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    status = models.CharField(max_length=1, choices=REQUEST_STATUS, default='0')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('passenger', 'ride')
        ordering = ['-created_on']

    def __str__(self):
        return f"Ride ID:{self.ride.id} | RideRequest by {self.passenger.username} for ride from {self.ride.origin} to {self.ride.destination} - Status: {self.get_status_display()}"