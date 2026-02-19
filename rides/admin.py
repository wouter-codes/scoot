from django.contrib import admin
from .models import Rides, RideRequest, UserProfile

class RideRequestAdmin(admin.ModelAdmin):
    """Admin interface for RideRequest with seat management."""
    
    def save_model(self, request, obj, form, change):
        """Decrement seats when creating a new ride request."""
        if not change:  # Only for new requests
            obj.ride.seats_available -= obj.seats_requested
            obj.ride.save()
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Restore seats when deleting a ride request."""
        obj.ride.seats_available += obj.seats_requested
        obj.ride.save()
        super().delete_model(request, obj)

# Register your models here.
admin.site.register(Rides)
admin.site.register(RideRequest, RideRequestAdmin)
admin.site.register(UserProfile)