from django import forms
from .models import Ride, DriverUser, RiderUser, UserSelection
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

STATUS_OPTIONS = [('open', 'open'), ('confirmed', 'Confirmed'), ('complete', 'Complete')]
USER_TYPES = [('ride owner', 'Ride Owner'), ('ride sharer', 'Ride Sharer'), ('driver', 'Driver')]


class UserSignUpForm(UserCreationForm):
    # user_type = forms.CharField(label='Please select user type', widget=forms.Select(choices=USER_TYPES))
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'password1',
                  'password2')

    def save(self, commit=True):
        user = super(UserSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            print(user.email, user.username, user.password)
        return user
    # class Meta:
    #     model = RideShareUser
    #     fields = ('username',
    #               'email',
    #               'password1',
    #               'password2')


class UserSelectionForm(forms.ModelForm):
    user_type = forms.CharField(label='Please select user type', widget=forms.Select(choices=USER_TYPES))

    class Meta:
        model = UserSelection
        fields = ['user_type']


class RideForm(forms.ModelForm):
    # vehicle_type_requested = forms.CharField(help_text="(Optional)", required=False)
    class Meta:
        model = Ride
        exclude = ['rider_owner_user_id']
        fields = ['destination',
                  'arrival_time',
                  'shareable',
                  'passengers_requested',
                  'vehicle_type_requested']
        widgets = { 'arrival_time': forms.TimeInput(attrs={'type': 'time'}) }

class DriverUserForm(forms.ModelForm):

    class Meta:
        model = DriverUser
        exclude = ['user']
        fields = ['license_plate_num',
                  'vehicle_model',
                  'passenger_seats_in_car']


class RiderUserForm(forms.ModelForm):
    class Meta:
        model = RiderUser
        fields = ['user_type',
                  'active_ride']
