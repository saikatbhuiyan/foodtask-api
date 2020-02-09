from django import forms
from django.contrib.auth.models import User

from . import models

class UserForm(forms.ModelForm):
  """Creating the form for user sigin up"""
  email = forms.CharField(max_length=100, required=True)
  password = forms.CharField(widget=forms.PasswordInput())

  class Meta:
    model = User
    fields = ("username", "email", "password")

class RestaurantForm(forms.ModelForm):
  """Creating the form for restaurant sigin up"""
  class Meta:
    model = models.Restaurant
    fields = ("name", "phone", "address", "logo")



