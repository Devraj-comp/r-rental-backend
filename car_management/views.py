from django.shortcuts import render
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Car, CarService, TourPackage, Booking, ServiceBooking, TourBooking
from .serializers import CarSerializer,BookingDetailSerializer, ServiceBookingDetailSerializer,  ServiceReadSerializer, ServiceWriteSerializer, TourPackageWriteSerializer, TourPackageReadSerializer, BookingSerializer, ServiceBookingSerializer, TourBookingSerializer, TourBookingDetailSerializer
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.authentication import JWTAuthentication

# CAR MANAGEMENT
# create car
class CarCreateView(generics.CreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

# list car
# class CarListView(generics.ListAPIView):
#     queryset = Car.objects.all()
#     serializer_class = CarSerializer
#     http_method_names = ['get']

# list each car
class CarListView(generics.ListAPIView):
    serializer_class = CarSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Car.objects.all()
        car_ids = self.request.query_params.get('ids', None)

        if car_ids:
            try:
                car_id_list = [int(id.strip()) for id in car_ids.split(', ')]
                queryset = queryset.filter(id__in = car_id_list)
            except:
                raise ValidationError({"Error": "Invalid car id"})
        return queryset
# update car
class CarUpdateView(generics.UpdateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

# delete car
class CarDeleteView(generics.DestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']

# available cars
from django.utils.dateparse import parse_date

class AvailableCarListView(generics.ListAPIView):
    serializer_class = CarSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Car.objects.all()
        
        # Get query parameters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if not start_date or not end_date:
            raise ValidationError({"error": "Both 'start_date' and 'end_date' are required."})

        try:
            # Parse the dates
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            if not start_date or not end_date or start_date > end_date:
                raise ValidationError({"error": "Invalid date range."})

            # Filter unavailable cars
            unavailable_cars = Booking.objects.filter(
                start_date__lte=end_date,  # Booking starts before or on the input end_date
                end_date__gte=start_date  # Booking ends after or on the input start_date
            ).values_list('car_id', flat=True)

            # Exclude unavailable cars to find available cars
            queryset = queryset.exclude(id__in=unavailable_cars)

        except Exception as e:
            raise ValidationError({"error": str(e)})

        return queryset


# SERVICES MANAGEMENT
# create car-service
class ServiceCreateView(generics.CreateAPIView):
    queryset = CarService.objects.all()
    serializer_class = ServiceWriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

# list car-services
class ServiceListView(generics.ListAPIView):
    queryset = CarService.objects.all()
    serializer_class = ServiceReadSerializer
    http_method_names = ['get']

# update car-services
class ServiceUpdateView(generics.UpdateAPIView):
    queryset = CarService.objects.all()
    serializer_class = ServiceWriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

# delete car-services
class ServiceDeleteView(generics.DestroyAPIView):
    queryset = CarService.objects.all()
    serializer_class = ServiceWriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']

# TOUR PACKAGES MANAGEMENT
# create tour-packages
class PackageCreateView(generics.CreateAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageWriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

# # list tour-packages
class PackageListView(generics.ListAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageReadSerializer
    http_method_names = ['get']

# # update tour-packages
class PackageUpdateView(generics.UpdateAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageWriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

# # delete tour-packages
class PackageDeleteView(generics.DestroyAPIView):
    queryset = TourPackage.objects.all()
    serializer_class = TourPackageWriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']

# Normal Booking management
# create booking
import logging
class BookingCreateView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

    def perform_create(self, serializer):
        """Override to auto-add the logged-in user."""
        user = self.request.user
        if user.is_authenticated:
            logging.info(f"Creating a booking for user: {user}")
            serializer.save(user=user)  # Automatically attach the logged-in user
        else:
            logging.error("Attempt to create booking without authentication.")
            raise serializers.ValidationError("User is not authenticated.")

    def create(self, request, *args, **kwargs):
        """Custom create method for better response handling."""
        logging.info(f"Authorization Header: {request.headers.get('Authorization')}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {"message": "Booking created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
# booking detail view
class BookingDetailView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingDetailSerializer  # Use for retrieving bookings with car details
    lookup_field = 'id'
# for admin
# update the booking status
class UpdateBookingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            status_value = request.data.get('status')
            if status_value not in ['Pending', 'Confirmed', 'Cancelled']:
                return Response({"error": "Invalid status value. "}, status=status.HTTP_400_BAD_REQUEST)
            booking.status = status_value
            booking.save()
            return Response({"message": "Booking status updated."}, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found. "}, status=status.HTTP_404_NOT_FOUND)

# list filtered booking for user
class BookingListView(generics.ListAPIView):
    serializer_class = BookingDetailSerializer
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # return bookings for the authenticated user.
        user = self.request.user
        return Booking.objects.filter(user=user)

class UpdateStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, pk):
        """
        Update the status of a booking by its ID (pk).
        """
        try:
            # Fetch the booking by its primary key
            booking = Booking.objects.get(pk=pk)

            # Extract the new status from the request data
            new_status = request.data.get("status")

            if not new_status:
                return Response(
                    {"error": "The 'status' field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the status and save the booking
            booking.status = new_status
            booking.save()

            # Return the updated booking as a response
            return Response(
                {
                    "id": booking.id,
                    "status": booking.status,
                },
                status=status.HTTP_200_OK,
            )

        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
# udpate booking
class BookingUpdateView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

# delete booking
class BookingDeleteView(generics.DestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']

# Services Booking management
# create booking
# class ServiceBookingCreateView(generics.CreateAPIView):
#     queryset = ServiceBooking.objects.all()
#     serializer_class = ServiceBookingSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [JWTAuthentication]
#     http_method_names = ['post']
class ServiceBookingCreateView(generics.CreateAPIView):
    queryset = ServiceBooking.objects.all()
    serializer_class = ServiceBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    http_method_names = ['post']

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            logging.info(f"Creating service booking for user: {user}")
            serializer.save(user=user)
        else:
            logging.error("Attempt to create service booking without authentication")
            raise serializers.ValidationError("User is not authenticated.")
    def create(self, request, *args, **kwargs):
        logging.info(f"Authentication Header: {request.headers.get('Authorization')}")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Booking created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


# list booking
class ServiceBookingListView(generics.ListAPIView):
    # queryset = ServiceBooking.objects.all()
    serializer_class = ServiceBookingDetailSerializer
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return ServiceBooking.objects.filter(user=user)

# service booking detail view
class ServiceBookingDetailView(generics.ListAPIView):
    queryset = ServiceBooking.objects.all()
    serializer_class = ServiceBookingDetailSerializer  # Use for retrieving bookings with car details
    lookup_field = 'id'

# udpate booking
class ServiceBookingUpdateView(generics.UpdateAPIView):
    queryset = ServiceBooking.objects.all()
    serializer_class = ServiceBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

# delete booking
class ServiceBookingDeleteView(generics.DestroyAPIView):
    queryset = ServiceBooking.objects.all()
    serializer_class = ServiceBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']



# create tour package
class TourBookingCreateView(generics.CreateAPIView):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]
    http_method_names = ['post']

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            logging.info(f"Creating service booking for user: {user}")
            serializer.save(user=user)
        else:
            logging.error("Attempt to create service booking without authentication")
            raise serializers.ValidationError("User is not authenticated.")
    def create(self, request, *args, **kwargs):
        logging.info(f"Authentication Header: {request.headers.get('Authorization')}")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Booking created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


# list booking
class TourBookingListView(generics.ListAPIView):
    serializer_class = TourBookingDetailSerializer
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return TourBooking.objects.filter(user=user)

# tour booking detail view
class TourBookingDetailView(generics.ListAPIView):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingDetailSerializer  # Use for retrieving bookings with car details
    lookup_field = 'id'

# udpate booking
class TourBookingUpdateView(generics.UpdateAPIView):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

# delete booking
class TourBookingDeleteView(generics.DestroyAPIView):
    queryset = TourBooking.objects.all()
    serializer_class = TourBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']
