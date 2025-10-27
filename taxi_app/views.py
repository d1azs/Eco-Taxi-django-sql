from django.shortcuts import render, redirect, get_object_or_404
from .models import Car
from math import radians, sin, cos, sqrt, atan2
import random  # Для генерації номерів

# Координати адрес
ADDRESS_COORDS = {
    'Rynok Square, Lviv': (49.841952, 24.0315921),
    'Lviv Opera House, Lviv': (49.8441, 24.0264),
    'High Castle, Lviv': (49.8423, 24.0370),
    'Lviv Railway Station, Lviv': (49.8403, 23.9943),
    'Lviv Airport, Lviv': (49.8125, 23.9561),
    'Stryisky Park, Lviv': (49.8231, 24.0213),
    'Shevchenkivskyi Hai, Lviv': (49.845, 24.004),
    'Potocki Palace, Lviv': (49.839, 24.030),
    'Lychakiv Cemetery, Lviv': (49.832, 24.055),
    'Prospect Svobody, Lviv': (49.844, 24.026),
    'Ryasne, Lviv': (49.8742, 23.9494),
}

# Функція для обчислення відстані
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(float(lat1) - float(lat2))
    dlon = radians(float(lon1) - float(lon2))
    a = sin(dlat / 2)**2 + cos(radians(float(lat1))) * cos(radians(float(lat2))) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Середня швидкість 30 км/год
AVERAGE_SPEED = 30.0
def calculate_time(distance_km):
    hours = distance_km / AVERAGE_SPEED
    return int(hours * 60)

def home(request):
    return render(request, 'taxi_app/home.html')

def about(request):
    return render(request, 'taxi_app/about.html')

def order(request):
    error = None
    if request.method == 'POST':
        selected_car_id = request.POST.get('selected_car')
        if selected_car_id:
            if 'pickup_address' in request.session and 'dropoff_address' in request.session:
                request.session['selected_car_id'] = selected_car_id
                return redirect('order_confirmation')
            else:
                error = 'Спочатку виберіть адреси.'
                return render(request, 'taxi_app/order.html', {'error': error})
    
        pickup_address = request.POST.get('pickup_address')
        dropoff_address = request.POST.get('dropoff_address')
        
        if not pickup_address or not dropoff_address:
            error = 'Виберіть обидві адреси.'
        elif pickup_address not in ADDRESS_COORDS or dropoff_address not in ADDRESS_COORDS:
            error = 'Адреса не знайдена.'
        else:
            pickup_lat, pickup_lon = ADDRESS_COORDS[pickup_address]
            dropoff_lat, dropoff_lon = ADDRESS_COORDS[dropoff_address]
            
            request.session['pickup_address'] = pickup_address
            request.session['dropoff_address'] = dropoff_address
            request.session['pickup_lat'] = pickup_lat
            request.session['pickup_lon'] = pickup_lon
            request.session['dropoff_lat'] = dropoff_lat
            request.session['dropoff_lon'] = dropoff_lon
            
            return redirect('cars')
    
    return render(request, 'taxi_app/order.html', {'error': error})

def cars(request):
    if 'pickup_lat' not in request.session:
        return redirect('order')
    
    pickup_lat = float(request.session['pickup_lat'])
    pickup_lon = float(request.session['pickup_lon'])
    dropoff_lat = float(request.session['dropoff_lat'])
    dropoff_lon = float(request.session['dropoff_lon'])
    pickup_address = request.session['pickup_address']
    dropoff_address = request.session['dropoff_address']
    
    distance = haversine(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
    request.session['distance'] = distance

    available_cars = []
    for car in Car.objects.all():
        if car.latitude and car.longitude:
            car_distance = haversine(pickup_lat, pickup_lon, float(car.latitude), float(car.longitude))
            if car_distance <= 5:
                car.arrival_time = calculate_time(car_distance)
                available_cars.append(car)
    
    car_class = request.GET.get('class')
    if car_class:
        available_cars = [car for car in available_cars if car.car_class == car_class]
    
    trip_time = calculate_time(distance)
    request.session['trip_time'] = trip_time
    
    context = {
        'cars': available_cars,
        'classes': ['Econom', 'Comfort', 'Business'],
        'pickup_address': pickup_address,
        'dropoff_address': dropoff_address,
        'distance': distance,
        'trip_time': trip_time,
    }
    return render(request, 'taxi_app/cars.html', context)


def order_confirmation(request):
    selected_car_id = request.session.get('selected_car_id')
    if not selected_car_id:
        return redirect('order') 

    car = get_object_or_404(Car, pk=selected_car_id)
    
    distance = request.session.get('distance', 0)
    trip_time = request.session.get('trip_time', 0)
    pickup_lat = request.session.get('pickup_lat')
    pickup_lon = request.session.get('pickup_lon')
    dropoff_lat = request.session.get('dropoff_lat')
    dropoff_lon = request.session.get('dropoff_lon')
    pickup_address = request.session.get('pickup_address')
    dropoff_address = request.session.get('dropoff_address')

    if not all([distance, trip_time, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, pickup_address, dropoff_address]):
        return redirect('order')

    
    total_price = distance * float(car.price_per_km)
    
    car_distance = haversine(pickup_lat, pickup_lon, float(car.latitude), float(car.longitude))
    arrival_time = calculate_time(car_distance)

    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    license_plate = (random.choice(letters) + random.choice(letters) + 
                     str(random.randint(1000, 9999)) + 
                     random.choice(letters) + random.choice(letters))
    
 
    maps_api_key = 'API KEY'
    maps_url = (f"https://maps.googleapis.com/maps/api/staticmap?"
                f"size=400x300&path=color:0x0000ff|weight:5|"
                f"{pickup_lat},{pickup_lon}|{dropoff_lat},{dropoff_lon}&"
                f"markers=color:red|{pickup_lat},{pickup_lon}&"
                f"markers=color:green|{dropoff_lat},{dropoff_lon}&"
                f"key={maps_api_key}")
    
    context = {
        'car': car,
        'distance': distance,
        'trip_time': trip_time,
        'arrival_time': arrival_time,
        'license_plate': license_plate,
        'maps_url': maps_url,
        'pickup_address': pickup_address,
        'dropoff_address': dropoff_address,
        'total_price': total_price
    }

    if request.method == 'POST':
        request.session.pop('selected_car_id', None)
        request.session.pop('pickup_address', None)
        request.session.pop('dropoff_address', None)
        request.session.pop('distance', None)
        request.session.pop('trip_time', None)
        request.session.pop('pickup_lat', None)
        request.session.pop('pickup_lon', None)
        request.session.pop('dropoff_lat', None)
        request.session.pop('dropoff_lon', None)

        context['is_preview'] = False
        return render(request, 'taxi_app/order_confirmation.html', context)

    context['is_preview'] = True
    return render(request, 'taxi_app/order_confirmation.html', context)