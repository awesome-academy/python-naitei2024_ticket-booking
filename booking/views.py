from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import *
from .models import *
from django.shortcuts import render, get_object_or_404
from .models import Flight, Airport, FlightTicketType
from django.db.models import Min, Q, F
from . import constants
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from ticketbooking import settings


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

    # Filter flights by chair type and available seats
    departure_flights = (
        Flight.objects.filter(
            departure_airport=from_airport,
            arrival_airport=to_airport,
            departure_time__date=departure_date,
            flighttickettype__available_seats__gte=num_passengers,
            flighttickettype__ticket_type__name=chair_type_name,
        )
        .annotate(
            min_price=Min(
                "flighttickettype__price",
                filter=Q(flighttickettype__available_seats__gte=num_passengers),
            ),
            ticket_type_price=F(
                "flighttickettype__price"
            ),  # Get the specific price for the chair type
            flight_ticket_type_id=F("flighttickettype__flight_ticket_types_id"),
        )
        .order_by("min_price")
    )
    if not departure_flights:
        context["error_message"] = _(
            "No flights available with the selected criteria. Please try again."
        )
        return render(request, "homepage.html", context)

    if trip_type == "round":
        return_flights = Flight.objects.filter(
            departure_airport=to_airport,
            arrival_airport=from_airport,
            departure_time__date=return_date,
        ).order_by("base_price")
        context["return_flights"] = return_flights
    context["departure_flights"] = departure_flights

    # If round trip, get return flights with the same conditions
    if trip_type == "round":
        return_flights = (
            Flight.objects.filter(
                departure_airport=to_airport,
                arrival_airport=from_airport,
                departure_time__date=return_date,
                flighttickettype__available_seats__gte=num_passengers,
                flighttickettype__ticket_type__name=chair_type_name,
            )
            .annotate(
                min_price=Min(
                    "flighttickettype__price",
                    filter=Q(flighttickettype__available_seats__gte=num_passengers),
                ),
                ticket_type_price=F(
                    "flighttickettype__price"
                ),  # Get the specific price for the chair type
                flight_ticket_type_id=F("flighttickettype__flight_ticket_types_id"),
            )
            .order_by("min_price")
        )
        if not return_flights:
            context["error_message"] = _(
                "No return flights available with the selected criteria. Please try again."
            )
            return render(request, "homepage.html", context)
        context["return_flights"] = return_flights

    return render(request, "homepage.html", context)


def flight_detail(request, flight_id):
    flight = get_object_or_404(Flight, flight_id=flight_id)
    departure_airport = flight.departure_airport
    arrival_airport = flight.arrival_airport

    context = {
        "flight": flight,
        "departure_airport": departure_airport,
        "arrival_airport": arrival_airport,
    }

    return render(request, "flight_detail.html", context)


def flight_list(request):
    flights = Flight.objects.all()

    # Bộ lọc theo ngày khởi hành
    departure_date = request.GET.get("departure_date")
    if departure_date:
        flights = flights.filter(departure_time__date=departure_date)

    # Bộ lọc theo địa điểm khởi hành
    departure_location = request.GET.get("departure_location")
    if departure_location:
        flights = flights.filter(departure_airport__city=departure_location)

    # Lấy danh sách các thành phố từ model Airport
    airports = Airport.objects.values_list("city", flat=True).distinct()

    context = {
        "flights": flights,
        "airports": airports,
    }
    return render(request, "flight_list.html", context)


def verify_email(request, email):
    user = Account.objects.get(email=email)
    otp = OtpToken.objects.get(user=user)
    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data["otp"]
            if otp.otp == otp_entered:
                user.status = constants.STATUS_CHOICES[1][0]
                user.save()
                messages.success(request, _("Email verified successfully."))
                return HttpResponseRedirect(reverse("index"))
            else:
                messages.error(request, _("Invalid OTP. Please try again."))
                return render(
                    request, "verify_email.html", {"form": form, "email": email}
                )
        else:
            messages.error(request, _("Invalid OTP. Please try again."))
            return render(request, "verify_email.html", {"form": form, "email": email})
    else:
        form = VerifyEmailForm()
        return render(request, "verify_email.html", {"form": form, "email": email})

def select_flight(request):
    departure_id = request.GET.get("departureId")
    return_id = request.GET.get("returnId")
    num_passengers = int(request.GET.get("numPassengers", 1))  # Default to 1 if not provided

    # Initialize variables
    departure_flight_ticket_type = None
    return_flight_ticket_type = None

    # Check if departure_id is provided and get the FlightTicketType
    if departure_id:
        departure_id = int(departure_id)
        try:
            departure_flight_ticket_type = FlightTicketType.objects.get(flight_ticket_types_id=departure_id)
            if departure_flight_ticket_type.available_seats < num_passengers:
                messages.error(request, _("Not enough seats available for the selected departure flight."))
                return render(request, "index.html")
        except FlightTicketType.DoesNotExist:
            messages.error(request, _("Departure flight not found."))
            return redirect("index")

    # Check if return_id is provided and get the FlightTicketType
    if return_id:
        return_id = int(return_id)
        try:
            return_flight_ticket_type = FlightTicketType.objects.get(flight_ticket_types_id=return_id)
            if return_flight_ticket_type.available_seats < num_passengers:
                messages.error(request, _("Not enough seats available for the selected return flight."))
                return redirect("index")
        except FlightTicketType.DoesNotExist:
            messages.error(request, _("Return flight not found."))
            return redirect("index")
    
    return render(request, "inform.html", {
        'departure_flight_ticket_type': departure_flight_ticket_type,
        'return_flight_ticket_type': return_flight_ticket_type,
        'num_passengers': num_passengers,
    })
