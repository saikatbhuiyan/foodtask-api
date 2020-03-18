from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from . import forms
from . import models

def home(request):
  return redirect('restaurant-order')

"""Restaurant & Account"""

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


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
   return render(request, 'restaurant/home.html', {})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_account(request):
    """Edit restaurant and account"""
    user_form = forms.UserFormForEdit(instance = request.user)
    restaurant_form = forms.RestaurantForm(instance = request.user.restaurant)

    if request.method == "POST":
        user_form = forms.UserFormForEdit(request.POST, instance = request.user)
        restaurant_form = forms.RestaurantForm(request.POST, request.FILES, instance = request.user.restaurant)

        if user_form.is_valid() and restaurant_form.is_valid():
            user_form.save()
            restaurant_form.save()

    return render(request, 'restaurant/account.html', {
        "user_form": user_form,
        "restaurant_form": restaurant_form
    })

"""Restaurant & Account END"""

"""Restaurant MEALS"""

@login_required(login_url='/restaurant/sign-in/')
def restaurant_meal(request):
    meals = models.Meal.objects.filter(restaurant = request.user.restaurant).order_by("-id")
    return render(request, 'restaurant/meal.html', {"meals": meals})



@login_required(login_url='/restaurant/sign-in/')
def restaurant_add_meal(request):
    form = forms.MealForm()

    if request.method == "POST":
        form = forms.MealForm(request.POST, request.FILES)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant = request.user.restaurant
            meal.save()
            return redirect(restaurant_meal)

    return render(request, 'restaurant/add_meal.html', {
        "form": form
    })

@login_required(login_url='/restaurant/sign-in/')
def restaurant_edit_meal(request, meal_id):
    form = forms.MealForm(instance = models.Meal.objects.get(id = meal_id))

    if request.method == "POST":
        form = forms.MealForm(request.POST, request.FILES, instance = models.Meal.objects.get(id = meal_id))

        if form.is_valid():
            form.save()
            return redirect(restaurant_meal)

    return render(request, 'restaurant/edit_meal.html', {
        "form": form
    })


@login_required(login_url='/restaurant/sign-in/')
def restaurant_order(request):
    return render(request, 'restaurant/order.html', {})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    return render(request, 'restaurant/report.html', {})

