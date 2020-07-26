from .celery import app
from celery import group
import requests
import json
from redis_manager import RedisClient
import datetime

directions = [
    'ALA - TSE',
    'TSE - ALA',
    'ALA - MOW',
    'MOW - ALA',
    'ALA - CIT',
    'CIT - ALA',
    'TSE - MOW',
    'MOW - TSE',
    'TSE - LED',
    'LED - TSE']

from celery.schedules import crontab
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute="0"),
        check_update.s(),
    )

@app.task
def check_update():
    dt = datetime.datetime.now()
    hour = dt.hour
    if hour == 0:
        update_cache.delay()
    else:
        check_flights.delay()
        
@app.task
def update_cache():
    for d in directions:
        city_from, city_to = d.split(" - ")
        update_direction_upcoming_flights.delay(city_from, city_to)

@app.task
def check_flights():
    for direction in directions:
        dir_hash = RedisClient().get_direction_hash(direction)
        flights_to_check = []
        for dt, token in dir_hash.items():
            flight_result = RedisClient().get_flight_hash(token)
            if flight_result['is_valid']:
                flights_to_check.append((token, flight_result['price']))
        group(check_flight.s(token, price) for token, price in flights_to_check)()

@app.task(bind=True, default_retry_delay=300, max_retries=5)
def check_flight(self, booking_token, price):
    link = "https://booking-api.skypicker.com/api/v0.1/check_flights"
    
    params = {
        'v': 2,
        'booking_token': booking_token,
        'bnum': 1,
        'pnum': 1,
        'affily':'picky_us',
        'adults': 1
    }

    r = requests.get(link, params=params)
    data = json.loads(r.text)

    is_invalid = data.get('flights_invalid')
    is_checked = data.get('flights_checked')
    total = data.get('total')
    if is_invalid:
        RedisClient().invalidate_flight(booking_token)
        return
    else:
        if is_checked:
            RedisClient().check_flight(booking_token)
            if total != price:
                RedisClient().update_price(booking_token, total)
        else:
            check_flight.apply_async((booking_token, price), countdown=30)
            return data


@app.task(bind=True, default_retry_delay=300, max_retries=5)
def update_direction_upcoming_flights(self, city_from, city_to):
    link = "https://api.skypicker.com/flights"
    date_from = datetime.date.today()
    date_to = datetime.date.today() + datetime.timedelta(days=30)
    params = {
        'partner': 'picky',
        'fly_from': city_from,
        'fly_to': city_to,
        'date_from': date_from.strftime("%d/%m/%Y"),
        'date_to': date_to.strftime("%d/%m/%Y"),
        'one_per_date': 1
    }
    r = requests.get(link, params=params)
    answer = json.loads(r.text)
    data = answer.get('data')
    direction_hash = {}

    for flight_obj in data:
        raw_dt = flight_obj.get('dTime')
        dt = datetime.datetime.fromtimestamp(raw_dt).strftime("%d/%m/%Y")
        token = flight_obj.get('booking_token')
        price = flight_obj.get('price')

        direction_hash[dt] = token
        RedisClient().update_flight(token, city_from, city_to, dt, price)

    RedisClient().update_direction("{0} - {1}".format(city_from, city_to), direction_hash)
    return data