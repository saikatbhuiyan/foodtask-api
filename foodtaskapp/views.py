from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from . import forms

def home(request):
  return redirect(restaurant_home)

@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
   return render(request, 'restaurant/home.html', {})


def restaurant_sign_up(request):
  user_form = forms.UserForm()
  restaurant_form = forms.RestaurantForm()

  if request.method == "POST":
    user_form = forms.UserForm(request.POST)
    restaurant_form = forms.RestaurantForm(request.POST, request.FILES)
    
    if user_form.is_valid() and restaurant_form.is_valid():
      new_user = User.objects.create_user(**user_form.cleaned_data)
      new_restaurant = restaurant_form.save(commit=False)
      new_restaurant.user = new_user
      new_restaurant.save()

      login(request, authenticate(
        username = user_form.cleaned_data["username"],
        password = user_form.cleaned_data["password"]
      ))

      return redirect(restaurant_home)

  context = {
    'user_form':user_form,
    'restaurant_form':restaurant_form,
  }
  
  return render(request, 'restaurant/sign_up.html', context )