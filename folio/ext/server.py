# -*- coding: utf-8 -*-
"""
    Folio local development web server.
"""

import os
import time
import thread

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ForkingMixIn


__all__ = ['run']
__version__ = '0.1'


class FolioHTTPServer(HTTPServer, ForkingMixIn, object):
    """Folio's web server for local development."""

    @property
    def max_children(self):
        return 1

    def __init__(self, folio, *args, **kargs):
        self.folio = folio
        self.logger = self.folio.logger
        self.webdir = self.folio.build_path

        HTTPServer.__init__(self, *args, **kargs)

        self.logger.info('Serving %s', self.webdir)
        self.logger.info('Running at %s:%d', *self.server_address)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self.webdir, request, client_address, self)


class FolioHTTPRequestHandler(SimpleHTTPRequestHandler, object):
    """Request for FolioHTTPServer.

    This will serve files as SimpleHTTPRequestHandler but within the value of
    the wdir parameter.

    It uses the parent logger to log information.

    :param wdir: The web directory to serve.
    """

    @property
    def server_version(self):
        return 'FolioHTTPServer/' + __version__

    def __init__(self, wdir, *args, **kargs):
        self.cdir = os.getcwd()
        self.wdir = wdir

        SimpleHTTPRequestHandler.__init__(self, *args, **kargs)

    def translate_path(self, path):
        os.chdir(self.wdir)
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        os.chdir(self.cdir)
        return path

    def log_request(self, code='-', size='-'):
        self.server.logger.info('%s %s', str(code), self.requestline)

    def log_error(self, message, *args):
        self.server.logger.error(message, *args)

    def log_message(self, message, *args):
        self.server.logger.debug(message, *args)


def run(folio, host='127.0.0.1', port=8080):
    """Runs the project on a local development server.

    :param host: The hostname to listen on.
    :param port: The port of the server.
    :param debug: If debug is enabled.
    """

    def serve():
        """Create a FolioHTTPServer and serve forever."""
        server = FolioHTTPServer(folio, (host, port), FolioHTTPRequestHandler)
        server.serve_forever()

    def watch(interval=1):
        """Loop template list looking for file changes in the modified time,
        and rebuild the template if necessary.

        Copyright notice.  This function is based in `werkzeug.serving`.

        :param interval: The time in seconds to wait between loops.
        """
        mtimes = {}
        while True:
            for template_name in folio.list_templates():
                filename = os.path.join(folio.source_path, template_name)
                otime = mtimes.get(filename)
                mtime = os.path.getmtime(filename)
                mtimes[filename] = mtime
                if otime is None:
                    continue
                elif mtime > otime:
                    folio.logger.info('Template %s modified' % template_name)
                    folio.build_template(template_name)
            time.sleep(interval)

    thread.start_new_thread(serve, ())

    try:
        watch()
    except KeyboardInterrupt:
        pass
