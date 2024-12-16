from django.contrib import admin
from .models import *


# model registration
admin.site.register(Car)
admin.site.register(CarService)
admin.site.register(TourPackage)
admin.site.register(Booking)
admin.site.register(ServiceBooking)
admin.site.register(TourBooking)