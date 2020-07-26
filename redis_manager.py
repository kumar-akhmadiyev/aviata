import redis
import json

class RedisClient(object):
    __instance = None
    _conn = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(
                RedisClient, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True)

    @property
    def conn(self):
        if self._conn is None:
            self.get_connection()
        return self._conn

    def get_connection(self):
        self._conn = redis.Redis(connection_pool= self.pool)

    def get_flight_hash(self, token):
        key = "flight:{0}".format(token)
        result = self.conn.hgetall(key)
        result['is_checked'] = True if result['is_checked'] == "1" else False
        result['is_valid'] = True if result['is_valid'] == "1" else False
        return result

    def get_direction_hash(self, direction):
        result = self.conn.hgetall(direction)
        return result

    def check_flight(self, token):
        key = "flight:{0}".format(token)
        self.conn.hset(key, "is_checked", 1)

    def invalidate_flight(self, token):
        key = "flight:{0}".format(token)
        self.conn.hset(key, "is_valid", 0)

    def update_price(self, token, new_price):
        key = "flight:{0}".format(token)
        self.conn.hset(key, "price", new_price)

    def update_direction(self, direction, data):
        """ data - hash with 'date_string': 'booking_token' format"""
        key = direction
        self.conn.hmset(key, data)

    def update_flight(self, token, from_city, to_city, flight_date, price, is_checked=False, is_valid=True):
        key = "flight:{0}".format(token)
        is_checked = 1 if is_checked else 0
        is_valid = 1 if is_valid else 0
        data = {
            "from_city": from_city,
            "to_city": to_city,
            "date": str(flight_date),
            "price": price,
            "is_checked": is_checked,
            "is_valid": is_valid
        }
        self.conn.hmset(key, data)