from tornado.httpserver import HTTPServer
from tornado import web, ioloop
from tornado.log import app_log
from .proxyhandlers import _make_serverproxy_handler
import click
import re
import os
import logging
from jupyterhub.services.auth import HubOAuthCallbackHandler, HubOAuth
from .util import url_path_join

def make_app(destport, prefix, command):

    proxy_handler = _make_serverproxy_handler('mainprocess', command, {}, 10, False, destport, {})

    return web.Application([
        (
            url_path_join(prefix, 'oauth_callback'),
            HubOAuthCallbackHandler,
        ),
        (
            r"^"+re.escape(prefix)+r"(.*)",
            proxy_handler,
            dict(state={})
        )
    ],
    debug=True,
    cookie_secret=os.urandom(32)
    )


@click.command()
@click.option('--port', default=8888, help='port for the proxy server to listen on')
@click.option('--destport', default=8500, help='port that the webapp should end up running on')
@click.option('--ip', default=None, help='Address to listen on')
@click.option('--debug/--no-debug', default=False, help='To display debug level logs')
@click.argument('command', nargs=-1, required=True)
def run(port, destport, ip, debug, command):

    if debug:
        print('Setting debug')
        app_log.setLevel(logging.DEBUG)

    prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')

    app = make_app(destport, prefix, list(command))

    http_server = HTTPServer(app)

    http_server.listen(port, ip)

    print("Starting jhsingle-native-proxy server on address {} port {}, proxying to port {}".format(ip, port, destport))
    print("URL Prefix: {}".format(prefix))
    print("Command: {}".format(command))
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
