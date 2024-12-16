from django.db import models
from django.contrib.auth.models import User

# car model
class Car(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    manufacturing_year = models.CharField(max_length=100)
    license_number = models.CharField(max_length=250)
    available = models.BooleanField(default=True)
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=50, choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric')])
    image = models.ImageField(blank=True, null=True, upload_to='cars/')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    seat_capacity = models.IntegerField(default=4)
    color = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100)
    current_status = models.CharField(max_length=50, default='Available')
    last_serviced_date = models.DateField(null=True, blank=True)
    insurance_included = models.BooleanField(default=False)
    extras = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.make} {self.model} ({self.manufacturing_year})'

# service_packages model
class CarService(models.Model):
    service = models.CharField(max_length=100)
    cars = models.ManyToManyField(Car, related_name='service', blank=True)

    def __str__(self):
        return f"Service: {self.service}"
    
# tour_packages model
class TourPackage(models.Model):
    package = models.CharField(max_length=250)
    duration = models.CharField(max_length=50)
    price = models.IntegerField()
    cars = models.ManyToManyField(Car, related_name='tour_package', blank=True)

    def __str__(self):
        return f"TourPackage: {self.package}"
    
# default booking model
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')])

    def __str__(self):
        return f"{self.user.username} - {self.car.model} - {self.start_date}"

# service booking model
class ServiceBooking(models.Model):
    service = models.ForeignKey(CarService, on_delete=models.CASCADE, related_name='service_bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending')

    def __str__(self):
        return f"Booking for {self.service.service} by {self.user}"
    
# tour booking model
class TourBooking(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='tour_bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending')


    def __str__(self):
        return f"Booking for {self.package.package} by {self.user}"