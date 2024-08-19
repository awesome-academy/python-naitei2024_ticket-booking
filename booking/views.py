from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import *
from .models import *

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _("You've been logged in successfully"))
                return HttpResponseRedirect(reverse("index"))
            else:
                messages.error(request, _("Invalid username and/or password"))
                return render(request, "login.html", {'form': form})
        else:
            messages.error(request, _("This username is not valid. Username should contain alphanumeric characters only."))
            return render(request, "login.html", {'form': form})
    else:
        form = LoginForm()
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                account = form.save(commit=False)
                account.set_password(form.cleaned_data["password"])
                account.save()
            except:
                messages.error(request, _("Username already exists"))
                return render(request, "register.html", {'form': form})
            account = authenticate(request, username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            login(request, account)
            return redirect('index')
        else:
            messages.error(request, _("Information is not valid. Please check information again."))
            return render(request, "register.html", {'form': form})
    else:
        form = SignUpForm()
        return render(request, "register.html", {'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
from django.shortcuts import render
from booking.models import Airport, Flight
import json


def get_airports():
    """Retrieve all airports from the database."""
    airports = Airport.objects.all().values("airport_code", "name", "city", "country")
    return list(airports)


def index(request):
    trip_type = request.GET.get("tripType")
    from_airport = request.GET.get("from")
    to_airport = request.GET.get("to")
    departure_date = request.GET.get("departureDate")
    return_date = request.GET.get("returnDate")

    context = {
        "trip_type": trip_type,
        "from_airport": from_airport,
        "to_airport": to_airport,
        "departure_date": departure_date,
        "return_date": return_date,
        "airports": json.dumps(get_airports()),
    }

    if (
        not from_airport
        or not to_airport
        or not departure_date
        or (trip_type == "round" and not return_date)
    ):
        return render(request, "homepage.html", context)

    if from_airport == to_airport:
        return render(request, "homepage.html", context)

    departure_flights = Flight.objects.filter(
        departure_airport=from_airport,
        arrival_airport=to_airport,
        departure_time__date=departure_date,
    ).order_by("base_price")

    if trip_type == "round":
        return_flights = Flight.objects.filter(
            departure_airport=to_airport,
            arrival_airport=from_airport,
            departure_time__date=return_date,
        ).order_by("base_price")
        context["return_flights"] = return_flights
    context["departure_flights"] = departure_flights

    return render(request, "homepage.html", context)
