from api.api_client import APIClientAsync
from tornado_json.requesthandlers import APIHandler
from tornado_json.exceptions import api_assert
from tornado_json import gen


class BaseApiHandler(APIHandler):
    @gen.coroutine
    def _execute(self, transforms, *args, **kwargs):
        return super(BaseApiHandler, self)._execute(transforms, *args, **kwargs)

    @property
    def api_client(self):
        async_api = APIClientAsync()
        return async_api


class GetDirectionHash(BaseApiHandler):
    @gen.coroutine
    def get(self):
        from_city = self.get_argument('from_city', None)
        to_city = self.get_argument('to_city', None)
        direction = "{0} - {1}".format(from_city, to_city)
        print(direction)
        try:
            result = yield self.api_client.get_direction_hash(direction)
        except AssertionError as e:
            api_assert(False, 403, e.message)
        except Exception as e:
            self.error(e)
        else:
            self.success(result)
    __url_names__ = ['get_direction_hash']


class GetFlightsHash(BaseApiHandler):
    @gen.coroutine
    def get(self):
        from_city = self.get_argument('from_city', None)
        to_city = self.get_argument('to_city', None)
        direction = "{0} - {1}".format(from_city, to_city)

        try:
            result = yield self.api_client.get_flights_hash(direction)
        except AssertionError as e:
            api_assert(False, 403, e.message)
        except Exception as e:
            self.error(e)
        else:
            self.success(result)
    __url_names__ = ['get_flights_hash']


class CheckFlights(BaseApiHandler):
    @gen.coroutine
    def get(self):
        try:
            result = yield self.api_client.check_flights()
        except AssertionError as e:
            api_assert(False, 403, e.message)
        except Exception as e:
            self.error(e)
        else:
            self.success(result)
    __url_names__ = ['check_flights']

class UpdateCache(BaseApiHandler):
    @gen.coroutine
    def get(self):
        try:
            result = yield self.api_client.update_cache()
        except AssertionError as e:
            api_assert(False, 403, e.message)
        except Exception as e:
            self.error(e)
        else:
            self.success(result)
    __url_names__ = ['update_cache']    