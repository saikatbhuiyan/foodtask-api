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
    if request.method == "POST":
        order = models.Order.objects.get(id = request.POST["id"], restaurant = request.user.restaurant)

        if order.status == models.Order.COOKING:
            order.status = models.Order.READY
            order.save()

    orders = models.Order.objects.filter(restaurant = request.user.restaurant).order_by("-id")
    return render(request, 'restaurant/order.html', {"orders": orders})

@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    return render(request, 'restaurant/report.html', {})



##############
# DRIVERS
##############

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status = Order.READY, driver = None).order_by("-id"),
        many = True
    ).data

    return JsonResponse({"orders": orders})

@csrf_exempt
# POST
# params: access_token, order_id
def driver_pick_order(request):

    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        # Get Driver
        driver = access_token.user.driver

        # Check if driver can only pick up one order at the same time
        if Order.objects.filter(driver = driver).exclude(status = Order.DELIVERED):
            return JsonResponse({"status": "failed", "error": "You can only pick one order at the same time."})

        try:
            order = Order.objects.get(
                id = request.POST["order_id"],
                driver = None,
                status = Order.READY
            )
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This order has been picked up by another."})

    return JsonResponse({})

# GET params: access_token
def driver_get_latest_order(request):
    # Get token
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    driver = access_token.user.driver
    order = OrderSerializer(
        Order.objects.filter(driver = driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"order": order})

# POST params: access_token, order_id
@csrf_exempt
def driver_complete_order(request):
    # Get token
    access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
        expires__gt = timezone.now())

    driver = access_token.user.driver

    order = Order.objects.get(id = request.POST["order_id"], driver = driver)
    order.status = Order.DELIVERED
    order.save()

    return JsonResponse({"status": "success"})

# GET params: access_token
def driver_get_revenue(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())

    driver = access_token.user.driver

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver = driver,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day
        )

        revenue[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"revenue": revenue})

