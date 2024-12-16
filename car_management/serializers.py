from django.contrib.auth.models import Group, User
from user.models import UserProfile
from rest_framework import serializers
from user.serializers import UserSerializer, UserProfileSerializer

from .models import Car, CarService, TourPackage, Booking, ServiceBooking, TourBooking

# car serializer
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

# car-service serializer
class ServiceReadSerializer(serializers.ModelSerializer):
    cars = CarSerializer(many=True)
    class Meta:
        model = CarService
        fields = '__all__'

class ServiceWriteSerializer(serializers.ModelSerializer):
    # cars = CarSerializer(many=True, read_only = True)
    cars = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all(), many=True)
    class Meta:
        model = CarService
        fields = '__all__'


# tour-packages serializer
class TourPackageReadSerializer(serializers.ModelSerializer):
    cars = CarSerializer(many=True)
    class Meta:
        model = TourPackage
        fields = '__all__'

class TourPackageWriteSerializer(serializers.ModelSerializer):
    cars = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all(), many=True)
    class Meta:
        model = TourPackage
        fields = '__all__'

# car booking serializer
class BookingSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())
    # car = CarSerializer()
    # car = CarSerializer(many=True)
    class Meta:
        model = Booking
        fields = [
            'id',
            'start_date',
            'end_date',
            'start_location',
            'end_location',
            'status',
            'total_price',
            'car',
            'user',
        ]
        read_only_fields = ['total_price']
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End data must be after start date. ")
        
        # check car availability within the selected date range
        overlapping_bookings = Booking.objects.filter(
            car = data['car'],
            start_date__lt = data['end_date'],
            end_date__gt = data['start_date']
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError("This car is not available for the selected dates. ")

        return data
    def create(self, validated_data):
        # car_id = validated_data=['car']
        # car = Car.objects.get(id=car_id)
        car = validated_data['car']
        user = validated_data['user']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        days = (end_date - start_date).days
        total_price = days * car.price_per_day

        validated_data['total_price'] = total_price
        # validated_data['car'] = car
        return super().create(validated_data)
    
# nested booking response
class BookingDetailSerializer(serializers.ModelSerializer):
    car = CarSerializer()  # Use nested CarSerializer for output
    user = UserSerializer()
    class Meta:
        model = Booking
        fields = [
            'id',
            'start_date',
            'end_date',
            'start_location',
            'end_location',
            'status',
            'total_price',
            'car',
            'user',
        ]
# car-service booking serializer
# class ServiceBookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceBooking
#         fields = '__all__'

class ServiceBookingSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # service = serializers.PrimaryKeyRelatedField(queryset=ServiceReadSerializer.objects.all())
    class Meta:
        model = ServiceBooking
        fields = [
            'id',
            'service',
            'start_location',
            'end_location',
            'start_date',
            'end_date',
            'total_price',
            'status',
            'car',
            'user'
        ]
        read_only_fields = ['total_price']
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End data must be after start date. ")
        
        # check car availability within the selected date range
        overlapping_bookings = Booking.objects.filter(
            car = data['car'],
            start_date__lt = data['end_date'],
            end_date__gt = data['start_date']
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError("This car is not available for the selected dates. ")

        return data
    def create(self, validated_data):
        # car_id = validated_data=['car']
        # car = Car.objects.get(id=car_id)
        car = validated_data['car']
        user = validated_data['user']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        days = (end_date - start_date).days
        total_price = days * car.price_per_day

        validated_data['total_price'] = total_price
        # validated_data['car'] = car
        return super().create(validated_data)
# nested service booking
class ServiceBookingDetailSerializer(serializers.ModelSerializer):
    car = CarSerializer()  # Use nested CarSerializer for output
    user = UserSerializer()
    service = ServiceReadSerializer()
    class Meta:
        model = ServiceBooking
        fields = [
            'id',
            'service',
            'start_location',
            'end_location',
            'start_date',
            'end_date',
            'status',
            'total_price',
            'car',
            'user',
        ]

class TourBookingSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # service = serializers.PrimaryKeyRelatedField(queryset=ServiceReadSerializer.objects.all())
    class Meta:
        model = TourBooking
        fields = [
            'id',
            'package',
            'start_location',
            'end_location',
            'start_date',
            'end_date',
            'total_price',
            'duration',
            'status',
            'car',
            'user'
        ]
        read_only_fields = ['total_price']
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End data must be after start date. ")
        
        # check car availability within the selected date range
        overlapping_bookings = Booking.objects.filter(
            car = data['car'],
            start_date__lt = data['end_date'],
            end_date__gt = data['start_date']
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError("This car is not available for the selected dates. ")

        return data
    def create(self, validated_data):
        # car_id = validated_data=['car']
        # car = Car.objects.get(id=car_id)
        car = validated_data['car']
        user = validated_data['user']
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        days = (end_date - start_date).days
        total_price = days * car.price_per_day

        validated_data['total_price'] = total_price
        # validated_data['car'] = car
        return super().create(validated_data)
# nested service booking
class TourBookingDetailSerializer(serializers.ModelSerializer):
    car = CarSerializer()  # Use nested CarSerializer for output
    user = UserSerializer()
    package = TourPackageReadSerializer()
    class Meta:
        model = TourBooking
        fields = [
            'id',
            'package',
            'start_location',
            'end_location',
            'start_date',
            'end_date',
            'total_price',
            'duration',
            'status',
            'car',
            'user'
        ]