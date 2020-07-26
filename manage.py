from tornado_json.routes import get_routes
import api
import json
import tornado.web
import tornado.ioloop
from tornado_json.application import Application as BaseApplication
from tasks import tasks

class Application(BaseApplication):
    def __init__(self,routes,settings):
        super(Application,self).__init__(
                routes ,settings)

def main(port_num):

    routes = get_routes(api)

    print("Routes\n======\n\n" + json.dumps(
            [(url, repr(rh)) for url, rh in routes],
            indent=2)
        )

    application = Application(routes=routes, settings={
        'debug': True,
        })
    tasks.update_cache.delay()
    application.listen(port_num, address='0.0.0.0')
    tornado.ioloop.IOLoop.instance().start()
    

if __name__ == '__main__':
    main(8889)