"""RideSharingService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from user.views import select, signup, register request
from user import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('users/select/', views.select_user_session, name='select_user_session'),
    path('users/register/', views.register, name='register'),
    path('users/register/driver/', views.driver_registration, name='driver'),
    path('users/login/', views.login_user, name='login'),
    path('users/logout/', views.logout_user, name='logout'),
    path('users/edit/driver/<int:driver_id>', views.driver_profile_edit, name='driver_profile_edit'),
    path('rides/rider/view/', views.ride_selection, name='ride_selection'),
    path('rides/rider/new/', views.request_new_ride, name='request_new_ride'),
    path('rides/sharer/view/', views.ride_sharer_view, name='ride_sharer_view'),
    path('rides/sharer/search/', views.ride_sharer_search, name='ride_sharer_search'),
    path('rides/sharer/join/<int:ride_to_join_id>', views.ride_sharer_join, name='ride_sharer_join'),
    path('rides/edit/<int:ride_edit_id>', views.ride_edit, name='ride_edit'),
    path('rides/detail/<int:ride_id>', views.ride_detail, name='ride_detail'),
    path('rides/driver/view/', views.driver_ride_status_viewing, name='driver_ride_status_viewing'),
    path('rides/driver/open/', views.driver_ride_searching, name='driver_ride_searching'),
    path('rides/driver/confirm/<int:ride_confirm_id>', views.ride_confirm, name='ride_confirm'),
    path('rides/driver/complete/<int:ride_complete_id>', views.ride_complete, name='ride_complete'),
    path('submit/', views.new_ride_submit, name='new_ride_submit'),
]

