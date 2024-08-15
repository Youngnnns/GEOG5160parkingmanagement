# parking/views.py
import json
import math
import datetime
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .forms import RoadsideReservationForm, PublicReservationForm, UserRegisterForm
from .models import PublicParkingPricingModel1, PublicParkingPricingModel2, PublicParkingPricingModel3, \
    PublicParkingPricingModel4, ParkingLot
from django.conf import settings
from django.shortcuts import render, redirect
import logging
from datetime import datetime, timedelta
from django.core.mail import send_mail
from .tasks import set_reservation_end_task
from django.contrib.staticfiles import finders


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# get weekday
def get_weekday_name(date):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[date.weekday()]


def get_rate_for_period(day_of_week, time, rates):
    for rate in rates:
        if day_of_week in rate['day_of_week'].split(','):
            start_time = rate['start_time']
            end_time = rate['end_time']
            if start_time <= time < end_time:
                return rate
    return None


roadside_pricing = {
    'Electric or hydrogen or hybrid': {
        'weekday_hourly': 5.00,
        'weekday_15min': 1.25,
        'saturday_morning': 2.00,
        'saturday_afternoon': 0.00,
        'sunday': 0.00
    },
    'Petrol vehicles registered from 2005': {
        'weekday_hourly': 7.20,
        'weekday_15min': 1.80,
        'saturday_morning': 2.00,
        'saturday_afternoon': 0.00,
        'sunday': 0.00
    },
    'Diesel vehicles registered from 2015': {
        'weekday_hourly': 7.20,
        'weekday_15min': 1.80,
        'saturday_morning': 2.00,
        'saturday_afternoon': 0.00,
        'sunday': 0.00
    },
    'Other vehicles': {
        'weekday_hourly': 10.00,
        'weekday_15min': 2.50,
        'saturday_morning': 2.00,
        'saturday_afternoon': 0.00,
        'sunday': 0.00
    }
}


# Calculating on-street car park prices
def calculate_roadside_parking_fee(vehicle_type, start_time, end_time):
    # Ensure that the incoming time parameter is in string format
    if isinstance(start_time, datetime):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M')
    if isinstance(end_time, datetime):
        end_time = end_time.strftime('%Y-%m-%dT%H:%M')

    start = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    end = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')

    # Calculation of total duration (hours)
    total_hours = (end - start).total_seconds() / 3600
    # Ensures a maximum duration of 4 hours
    total_hours = min(total_hours, 4)
    full_hours = int(total_hours)
    remaining_minutes = (total_hours - full_hours) * 60

    # Calculate the number of 15-minute intervals
    additional_quarters = int(remaining_minutes / 15) + (1 if remaining_minutes % 15 > 0 else 0)

    day_of_week = start.weekday()
    total_price = 0

    pricing = roadside_pricing[vehicle_type]

    # Calculation of base hourly rate
    if day_of_week < 5:  # Mon-Fri
        hourly_rate = pricing['weekday_hourly']
        quarter_rate = pricing['weekday_15min']
    elif day_of_week == 5:  # Sat
        hourly_rate = pricing['saturday_morning'] if start.hour < 11 else pricing['saturday_afternoon']
        quarter_rate = 0.25 * hourly_rate
    else:  # Sun
        hourly_rate = pricing['sunday']
        quarter_rate = 0.25 * hourly_rate

    # Calculation of total costs
    total_price += full_hours * hourly_rate
    total_price += additional_quarters * quarter_rate

    return total_price


# calculate price model 1

def calculate_price_model1(start_time_str, end_time_str, rates):
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
    total_price = 0.0
    fixed_periods = set()
    current_time = start_time

    while current_time < end_time:
        day_of_week = current_time.strftime('%A')
        next_time = current_time + timedelta(hours=1)
        if next_time > end_time:
            next_time = end_time

        rate = get_rate_for_period(day_of_week, current_time.time(), rates)
        if rate is not None:
            if 'fixed' in rate and rate['fixed']:
                period_identifier = (rate['start_time'], rate['end_time'])
                if period_identifier not in fixed_periods:
                    total_price += float(rate['price'])
                    fixed_periods.add(period_identifier)
            else:
                total_price += float(rate['price'])
        current_time = next_time

    return total_price


# calculate price model 2
def calculate_price_model2(start_datetime_str, end_datetime_str, rates):
    start_datetime = parse_datetime(start_datetime_str)
    end_datetime = parse_datetime(end_datetime_str)

    def get_rate_for_time(query_time, rates):
        query_time = query_time.time()  # Get only the time part for comparison
        for rate in rates:
            start_time = rate['start_time']
            end_time = rate['end_time']
            # Adjust for overnight rates
            if start_time <= end_time:
                if start_time <= query_time < end_time:
                    return rate
            else:  # overnight crossing midnight
                if not (end_time <= query_time < start_time):
                    return rate
        return None  # if no rate is applicable

    total_price = 0.0
    current_time = start_datetime

    while current_time < end_datetime:
        rate = get_rate_for_time(current_time, rates)
        if rate is None:
            break  # no applicable rate found

        # Find the next boundary or the booking end time
        next_boundary = datetime.combine(current_time.date(), rate['end_time'])
        if rate['end_time'] < rate['start_time']:
            next_boundary += timedelta(days=(1 if current_time.time() >= rate['start_time'] else 0))

        period_end = min(next_boundary, end_datetime)

        # Compute hours and round up if needed
        hours = (period_end - current_time).total_seconds() / 3600
        hours_rounded = int(hours) if hours == int(hours) else int(hours) + 1

        total_price += hours_rounded * float(rate['price'])

        current_time = period_end

    return total_price


# calculate price model 3
def parse_datetime(datetime_str):
    for fmt in ('%Y-%m-%dT%H:%M', '%Y.%m.%d %H:%M'):
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    raise ValueError("No valid date format found for input.")


def calculate_price_model3(start_datetime_str, end_datetime_str, rates):
    start_datetime = parse_datetime(start_datetime_str)
    end_datetime = parse_datetime(end_datetime_str)
    total_price = 0

    current_time = start_datetime

    while current_time < end_datetime:
        next_day_start = datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)
        period_end = min(end_datetime, next_day_start)  # Calculated to midnight of the day or final end time

        # Calculate the number of hours in the current cycle and round upwards
        period_hours = math.ceil((period_end - current_time).total_seconds() / 3600)

        day_name = current_time.strftime('%A')
        # Find the matching price for the current date in the rate list
        applicable_rates = [rate for rate in rates if day_name in rate['day_of_week'].split(',')]

        # Iterate to find the corresponding rate to calculate the price
        day_price = 0
        for rate in applicable_rates:
            if period_hours <= rate['duration_hours']:
                day_price = rate['price']
                break

        if day_price == 0 and applicable_rates:
            # If no specific hours match is found, use the maximum hourly rate
            day_price = max(applicable_rates, key=lambda x: x['duration_hours'])['price']

        total_price += day_price
        current_time = period_end  # Move to the next calculation start point

    return total_price


# calculate price model4
def calculate_price_model4(start_datetime_str, end_datetime_str, rates):
    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
    total_price = 0
    current_time = start_datetime

    while current_time < end_datetime:
        # End of current date (midnight)
        next_day_start = datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)
        period_end = min(next_day_start, end_datetime)  # If the end time is before midnight, take the end time

        # Calculate the number of hours of parking in the current time period (round up)
        hours = math.ceil((period_end - current_time).total_seconds() / 3600)

        day_name = current_time.strftime('%A')
        # Find applicable rates based on length of parking and day of week
        applicable_rates = [
            rate for rate in rates if day_name in rate['day_of_week'].split(',') and hours <= rate['duration_hours']
        ]
        if applicable_rates:
            # If you find a suitable rate, apply the rate to calculate the price
            rate = sorted(applicable_rates, key=lambda x: x['duration_hours'])[0]  # Selection of the closest longer-term rate
            total_price += rate['price']
        else:
            # Additional processing or default processing may be required if appropriate rates are not available
            total_price += 0

        current_time = period_end  # Move to the start of the next day

    return total_price


@login_required
def reserve_parking(request, objectid):
    parking_lot = get_object_or_404(ParkingLot, objectid=objectid)
    is_roadside = objectid in range(1, 156)  # IDs 1 to 155 are off-street car parks

    if is_roadside:
        form_class = RoadsideReservationForm
    else:
        form_class = PublicReservationForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')

            # Inspection time limits (on-street car parks only)
            if is_roadside:
                if (end_time - start_time).total_seconds() > 4 * 3600:
                    messages.error(request, message='Reservation time cannot exceed 4 hours for roadside parking.')
                    return redirect('reserve_parking', objectid=objectid)

            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.parking_lot = parking_lot

            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M')
            end_time_str = end_time.strftime('%Y-%m-%dT%H:%M')

            if parking_lot.lot_type == 'roadside':
                vehicle_type = form.cleaned_data['vehicle_type']
                reservation.price = calculate_roadside_parking_fee(vehicle_type, start_time, end_time)
            else:
                if objectid in [157, 158, 159, 162]:
                    rates = list(PublicParkingPricingModel1.objects.filter(objectid=objectid).values())
                    reservation.price = calculate_price_model1(start_time_str, end_time_str, rates)
                elif objectid == 160:
                    rates = list(PublicParkingPricingModel2.objects.filter(objectid=objectid).values())
                    reservation.price = calculate_price_model2(start_time_str, end_time_str, rates)
                elif objectid in [161, 164]:
                    rates = list(PublicParkingPricingModel3.objects.filter(objectid=objectid).values())
                    reservation.price = calculate_price_model3(start_time_str, end_time_str, rates)
                elif objectid in [156, 163, 165]:
                    rates = list(PublicParkingPricingModel4.objects.filter(objectid=objectid).values())
                    reservation.price = calculate_price_model4(start_time_str, end_time_str, rates)

            reservation.save()
            parking_lot.available_spaces -= 1
            parking_lot.save()

            # Setting tasks to increase the number of available car parking spaces at the end of a booking
            set_reservation_end_task(reservation.id, end_time)

            send_reservation_email(reservation)  # Add logic for sending emails

            return redirect('home')
    else:
        form = form_class()

    return render(request, 'reserve.html', {'parking_lot': parking_lot, 'form': form})


def send_reservation_email(reservation):
    subject = 'Reservation Confirmation'
    if reservation.parking_lot.lot_type == 'roadside':
        message = f"""
    Dear {reservation.first_name},

Your reservation for the on-street parking lot has been confirmed.

Street: {reservation.parking_lot.street_name}
Address: {reservation.parking_lot.address}
Start Time: {reservation.start_time}
End Time: {reservation.end_time}
Vehicle Type: {reservation.vehicle_type}
Price￡: £{reservation.price}
Phone Number: {reservation.phone_number}
License Plate: {reservation.license_plate}

Best wishes,
Parking Management Team
"""
    else:
        message = f"""
Dear {reservation.first_name},

Your reservation for the public parking lot has been confirmed.

Car Park Name: {reservation.parking_lot.car_park_name}
Address: {reservation.parking_lot.address}
Postcode: {reservation.parking_lot.postcode}
Start Time: {reservation.start_time}
End Time: {reservation.end_time}
Price￡: £{reservation.price}
Phone Number: {reservation.phone_number}
License Plate: {reservation.license_plate}

Best wishes,
Parking Management Team
        """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [reservation.email],
        fail_silently=False,
    )


# Get Logger
logger = logging.getLogger('django')


# calculate price view
@csrf_exempt
def calculate_price_view(request):
    if request.method == 'POST':
        try:
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            vehicle_type = request.POST.get('vehicle_type', None)
            objectid = int(request.POST.get('objectid'))

            logger.info(f"Start Time: {start_time}")
            logger.info(f"End Time: {end_time}")
            logger.info(f"Vehicle Type: {vehicle_type}")
            logger.info(f"Object ID: {objectid}")

            # Parsing date strings
            start_time_str = start_time
            end_time_str = end_time

            # Calculate prices based on car park ID and vehicle type
            if objectid in range(1, 156):
                price = calculate_roadside_parking_fee(vehicle_type, start_time_str, end_time_str)
            elif objectid in [157, 158, 159, 162]:
                rates = list(PublicParkingPricingModel1.objects.filter(objectid=objectid).values())
                logger.info(f"Rates: {rates}")
                price = calculate_price_model1(start_time_str, end_time_str, rates)
            elif objectid == 160:
                rates = list(PublicParkingPricingModel2.objects.filter(objectid=objectid).values())
                logger.info(f"Rates: {rates}")
                price = calculate_price_model2(start_time_str, end_time_str, rates)
            elif objectid in [161, 164]:
                rates = list(PublicParkingPricingModel3.objects.filter(objectid=objectid).values())
                logger.info(f"Rates: {rates}")
                price = calculate_price_model3(start_time_str, end_time_str, rates)
            elif objectid in [156, 163, 165]:
                rates = list(PublicParkingPricingModel4.objects.filter(objectid=objectid).values())
                logger.info(f"Rates: {rates}")
                price = calculate_price_model4(start_time_str, end_time_str, rates)
            else:
                price = 0  # Default or error conditions

            # Retain two decimal places and round up
            price = round(price, 2)

            return JsonResponse({'price': price})
        except Exception as e:
            logger.error(f"Error calculating price: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def load_postcode_data():
    file_path = finders.find('json/City of London postcodes.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


postcodes_data = load_postcode_data()


def search_parking(request):
    postcode = request.GET.get('postcode')
    for feature in postcodes_data['features']:
        if feature['properties']['name'] == postcode:
            coordinates = feature['geometry']['coordinates']
            search_point = Point(coordinates[0], coordinates[1])
            parking_lots = ParkingLot.objects.filter(location__distance_lte=(search_point, D(km=1)))
            parking_data = []

            for lot in parking_lots:
                if lot.location.geom_type == 'Point':
                    parking_data.append({
                        'objectid': lot.objectid,
                        'location': [lot.location.y, lot.location.x],  # Latitude, Longitude
                        'lot_type': lot.lot_type,
                        'car_park_name': lot.car_park_name,
                        'address': lot.address,
                        'capacity': lot.capacity,
                        'available_spaces': lot.available_spaces,
                        'charges': lot.charges,
                        'postcode': lot.postcode,
                        'geom_type': 'Point'
                    })
                elif lot.location.geom_type == 'MultiPolygon':
                    parking_data.append({
                        'objectid': lot.objectid,
                        'location': [
                            [[coord[1], coord[0]] for coord in polygon.coords[0]]
                            for polygon in lot.location
                        ],
                        'lot_type': lot.lot_type,
                        'street_name': lot.street_name,
                        'address': lot.address,
                        'capacity': lot.capacity,
                        'available_spaces': lot.available_spaces,
                        'maximum_stay': lot.maximum_stay,
                        'electric_or_hydrogen_or_hybrid': lot.electric_or_hydrogen_or_hybrid,
                        'petrol_vehicles_registered_from_2005': lot.petrol_vehicles_registered_from_2005,
                        'diesel_vehicles_registered_from_2015': lot.diesel_vehicles_registered_from_2015,
                        'other_vehicles': lot.other_vehicles,
                        'saturday_am_price': lot.saturday_am_price,
                        'geom_type': 'MultiPolygon'
                    })

            return JsonResponse({'parking_lots': parking_data, 'center': [coordinates[1], coordinates[0]]})

    return JsonResponse({'error': 'Postcode not found'}, status=404)


# Home view, showing map and search box
def home(request):
    parking_lots = ParkingLot.objects.all()
    parking_data = []

    for lot in parking_lots:
        if lot.location.geom_type == 'Point':
            parking_data.append({
                'objectid': lot.objectid,
                'location': [lot.location.y, lot.location.x],  # latitude, longitude
                'lot_type': lot.lot_type,
                'car_park_name': lot.car_park_name,
                'address': lot.address,
                'capacity': lot.capacity,
                'available_spaces': lot.available_spaces,
                'charges': lot.charges,
                'postcode': lot.postcode,
                'geom_type': 'Point'
            })
        elif lot.location.geom_type == 'MultiPolygon':
            parking_data.append({
                'objectid': lot.objectid,
                'location': [
                    [[[coord[1], coord[0]] for coord in polygon.coords[0]] for polygon in lot.location],
                ],
                'lot_type': lot.lot_type,
                'street_name': lot.street_name,
                'address': lot.address,
                'capacity': lot.capacity,
                'available_spaces': lot.available_spaces,
                'maximum_stay': lot.maximum_stay,
                'electric_or_hydrogen_or_hybrid': lot.electric_or_hydrogen_or_hybrid,
                'petrol_vehicles_registered_from_2005': lot.petrol_vehicles_registered_from_2005,
                'diesel_vehicles_registered_from_2015': lot.diesel_vehicles_registered_from_2015,
                'other_vehicles': lot.other_vehicles,
                'saturday_am_price': lot.saturday_am_price,
                'geom_type': 'MultiPolygon'
            })

    return render(request, 'home.html', {'parking_data': json.dumps(parking_data)})
