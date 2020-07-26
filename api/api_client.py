from concurrent.futures import ThreadPoolExecutor
from tornado import concurrent, ioloop
from tasks import tasks
from redis_manager import RedisClient


class APIClientAsync(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(
                APIClientAsync, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.io_loop = ioloop.IOLoop.current()

    @concurrent.run_on_executor
    def get_direction_hash(self, direction):
        result = RedisClient().get_direction_hash(direction)
        print(result)
        return result

    @concurrent.run_on_executor
    def get_flights_hash(self, direction):
        flights = RedisClient().get_direction_hash(direction)
        answer = []
        for k,v in flights.items():
            flight_result = RedisClient().get_flight_hash(v)
            answer.append({v: flight_result})
        return answer

    @concurrent.run_on_executor
    def check_flights(self):
        tasks.check_flights.delay()
        return "Check flights function is started. You can check flights cache with get_direction_hash and get_flights_hash api functions"

    @concurrent.run_on_executor
    def update_cache(self):
        tasks.update_cache.delay()
        return "Update cache is started. You can check flights cache with get_direction_hash and get_flights_hash api functions"
