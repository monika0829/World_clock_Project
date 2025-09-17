
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")   # ✅ after login go to home (clock)
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def home_view(request):
    # ✅ redirect home → clock page
    return redirect("clock")


@login_required
def clock_view(request):
    # Step 1: Fetch countries + cities
    url = "https://countriesnow.space/api/v0.1/countries"
    response = requests.get(url)
    data = response.json()["data"]

    countries = [item["country"] for item in data]
    selected_country = None
    selected_city = None
    current_time = None
    cities = []

    if request.method == "POST":
        selected_country = request.POST.get("country")
        selected_city = request.POST.get("city")

        # Get cities for the selected country
        for item in data:
            if item["country"] == selected_country:
                cities = item["cities"]
                break

        if selected_city:
            # Step 2: Get city coordinates
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {"name": selected_city, "count": 1}
            geo_resp = requests.get(geo_url, params=geo_params)

            if geo_resp.status_code == 200 and geo_resp.json().get("results"):
                city_data = geo_resp.json()["results"][0]
                lat, lon = city_data["latitude"], city_data["longitude"]

                # Step 3: Find timezone automatically
                tf = TimezoneFinder()
                timezone_name = tf.timezone_at(lng=lon, lat=lat)

                if timezone_name:
                    tz = pytz.timezone(timezone_name)
                    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    current_time = "Timezone not found"
            else:
                current_time = "City not found"

    return render(request, "accounts/clock.html", {
        "countries": countries,
        "cities": cities,
        "selected_country": selected_country,
        "selected_city": selected_city,
        "current_time": current_time,
    })
