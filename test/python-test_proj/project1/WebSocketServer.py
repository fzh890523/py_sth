#!/bin/python
# coding: utf-8

import logging
import os.path
import uuid
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    socket_handlers = set()

    def __init__(self):
        super(self.__class__, self).__init_()
        self.client_id = None

    @property
    def is_authed(self):
        return self.client_id is not None

    def open(self):
        WebSocketHandler.socket_handlers.add(self)
        send_message('A new user has entered the chat room.')

    def on_close(self):
        WebSocketHandler.socket_handlers.remove(self)
        send_message('A user has left the chat room.')

    def on_message(self, message):
        send_message(message)

    def send_message(self, message):
        self.write(message)

    @classmethod
    def broadcast_message(cls, message):
        for handler in cls.socket_handlers.iteritems():
            handler.send_message(message)


def send_message(message):
    for handler in WebSocketHandler.socket_handlers:
        try:
            handler.write_message(message)
        except:
            logging.error('Error sending message', exc_info=True)


def main():
    settings = {
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static')
    }
    application = tornado.web.Application([
        # ('/', MainHandler),
        # ('/new-msg/', ChatHandler),
        ('/new-msg/_socket', WebSocketHandler)
    ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()