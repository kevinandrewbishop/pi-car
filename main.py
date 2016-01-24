from __future__ import division
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import datetime
from tornado import gen
import pifacedigitalio as p

piface = p.PiFaceDigital()
LEFT_PIN = 5
RIGHT_PIN = 6

from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)

client_message = '0,-90'
class Controller():
    def __init__(self):
        self.count = 0
        self.motor = True

    def increment(self):
        beta, gamma = [float(item) for item in client_message.split(',')]
        if gamma < -90 or gamma > 0:
            gamma = -90
        if abs(beta) > 90:
            beta = 0
        gamma = (gamma + 90)/90
        beta = (beta + 90)/180
        print 'beta: %s gamma: %s' %(beta, gamma)
        #return None
        self.count += 1
        if self.count > 20:
            self.count = 1
            global client_message
            client_message = '0,-90'
        left_power = gamma - (1-beta)
        right_power = 2 - gamma - beta
        if self.count/20 > left_power:
            piface.output_pins[LEFT_PIN].value = False
        else:
            piface.output_pins[LEFT_PIN].value = True
        if self.count/20 > right_power:
            piface.output_pins[RIGHT_PIN].value = False
        else:
            piface.output_pins[RIGHT_PIN].value = True
        #print for debugging purposes. Comment this out when ready print Self count is %s and client_message is %s and motor is %s" %(self.count, client_message, self.motor)


controller = Controller()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message("connected")

    def on_message(self, message):
        print 'message received %s' % message
        self.write_message('message received %s' % message)
        global client_message
        client_message = message

    def on_close(self):
        print 'connection closed'

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port,address='0.0.0.0')
    print "Listening on port:", options.port
    main_loop = tornado.ioloop.IOLoop.instance()
    #main_loop.add_timeout(datetime.timedelta(seconds=2), test)
    tornado.ioloop.PeriodicCallback(controller.increment, 1).start()
    main_loop.start()
