# parking/forms.py
from django import forms
from .models import Reservation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

VEHICLE_TYPE_CHOICES = [
    ('Electric or hydrogen or hybrid', 'Electric or hydrogen or hybrid'),
    ('Petrol vehicles registered from 2005', 'Petrol vehicles registered from 2005'),
    ('Diesel vehicles registered from 2015', 'Diesel vehicles registered from 2015'),
    ('Other vehicles', 'Other vehicles'),
]


class RoadsideReservationForm(forms.ModelForm):
    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPE_CHOICES)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    license_plate = forms.CharField(max_length=20, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time', 'vehicle_type', 'first_name', 'first_name', 'license_plate', 'phone_number', 'email']


class PublicReservationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    license_plate = forms.CharField(max_length=20, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time', 'first_name', 'first_name', 'license_plate', 'phone_number', 'email']


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
