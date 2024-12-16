from django.urls import path
from . import views

urlpatterns = [
    # cars management endponts
    path('cars/', views.CarListView.as_view(), name='car-list'),
    path('available-cars/', views.AvailableCarListView.as_view(), name='available-car-list'),
    path('cars/create/', views.CarCreateView.as_view(), name='car-create'),
    path('cars/update/<int:pk>', views.CarUpdateView.as_view(), name='car-update'),
    path('cars/delete/<int:pk>/', views.CarDeleteView.as_view(), name='car-delete'),
    
    # car-service management endpoints
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    path('services/create/', views.ServiceCreateView.as_view(), name='service-create'),
    path('services/update/<int:pk>/', views.ServiceUpdateView.as_view(), name='service-update'),
    path('services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='service-delete'),

    # tour-packages management endpoints
    path('packages/', views.PackageListView.as_view(), name='package-list'),
    path('packages/create/', views.PackageCreateView.as_view(), name='package-create'),
    path('packages/update/<int:pk>/', views.PackageUpdateView.as_view(), name='package-update'),
    path('packages/delete/<int:pk>/', views.PackageDeleteView.as_view(), name='package-delete'),

    # booking management endpoints
    path('bookings/', views.BookingListView.as_view(), name='bookings-list'),
    path('bookings/detail', views.BookingDetailView.as_view(), name='bookings-detail'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='bookings-create'),
    path('bookings/update/<int:pk>/', views.BookingUpdateView.as_view(), name='booking-update'),
    path('bookings/delete/<int:pk>/', views.BookingDeleteView.as_view(), name='booking-delete'),

    # booking status update
    path('bookings/<int:pk>/updatestatus/', views.UpdateStatusView.as_view(), name='bookingstatus-update'),

    # service booking management endpoints
    path('serviceBookings/', views.ServiceBookingListView.as_view(), name='service-bookings-list'),
    path('serviceBookings/detail', views.ServiceBookingDetailView.as_view(), name='service-bookings-detail-list'),    
    path('serviceBookings/create/', views.ServiceBookingCreateView.as_view(), name='service-bookings-create'),
    path('serviceBookings/update/<int:pk>/', views.ServiceBookingUpdateView.as_view(), name='service-booking-update'),
    path('serviceBookings/delete/<int:pk>/', views.ServiceBookingDeleteView.as_view(), name='service-booking-delete'),

    # package booking management endpoints
    path('tourBookings/', views.TourBookingListView.as_view(), name='service-bookings-list'),
    path('tourBookings/detail', views.TourBookingDetailView.as_view(), name='service-bookings-detail-list'),    
    path('tourBookings/create/', views.TourBookingCreateView.as_view(), name='service-bookings-create'),
    path('tourBookings/update/<int:pk>/', views.TourBookingUpdateView.as_view(), name='service-booking-update'),
    path('tourBookings/delete/<int:pk>/', views.TourBookingDeleteView.as_view(), name='service-booking-delete'),
]