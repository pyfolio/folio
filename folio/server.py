# -*- coding: utf-8 -*-
"""
    Folio local development web server.
"""

import os
import time
import urllib
import thread
import shutil

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ForkingMixIn

__all__ = ['run']
__version__ = '0.1'


class FolioHTTPServer(HTTPServer, ForkingMixIn, object):
    """Folio's web server for local development."""

    @property
    def max_children(self):
        return 1

    def __init__(self, folio, *args, **kwargs):
        self.folio = folio
        self.logger = self.folio.logger

        HTTPServer.__init__(self, *args, **kwargs)

        self.logger.info('Serving %s', self.folio.build_path)
        self.logger.info('Running at %s:%d', *self.server_address)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self.folio, request, client_address, self)


class FolioHTTPRequestHandler(BaseHTTPRequestHandler, object):
    """Request for FolioHTTPServer.

    This will serve files as SimpleHTTPRequestHandler but within the value of
    the folio parameter, used to extract the build path and the debug status.

    It uses the parent logger to log information.

    :param folio: The serving project.
    """

    #: Text allowed extensions.
    txt_extensions = {'.txt'    : 'text/plain',
                      '.html'   : 'text/html',
                      '.css'    : 'text/css',
                      '.js'     : 'text/javascript'}

    #: Binary allowed extensions.
    bin_extensions = {'.png'    : 'image/png',
                      '.gif'    : 'image/gif',
                      '.jpeg'   : 'image/jpeg',
                      '.jpg'    : 'image/jpeg',
                      '.ico'    : 'image/x-icon'}

    #: All the allowed extensions.
    extensions = {}
    extensions.update(txt_extensions)
    extensions.update(bin_extensions)

    @property
    def server_version(self):
        return 'FolioHTTPServer/' + __version__

    def __init__(self, folio, request, client_address, server):
        self.wpath = folio.build_path
        self.debug = folio.config['DEBUG']

        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        """Serve a GET request."""
        path = self.send_headers()
        if path:
            _, ext = os.path.splitext(path)
            fmode = 'rb' if ext in self.bin_extensions else 'r'
            f = open(path, fmode)

            if ext in self.bin_extensions:
                shutil.copyfileobj(f, self.wfile)
            else:
                content = f.read()

                self.wfile.write(content)

            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        self.send_headers()

    def send_headers(self):
        """Based on SimpleHTTPRequestHandler.send_head, but doesn't send the
        header `Content-Length`. This is because if it's a text file, the
        method `do_GET` want to change it contexts."""
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            path = os.path.join(path, 'index.html')

        _, ext = os.path.splitext(path)
        if ext not in self.extensions:
            return self.send_error(403, 'Forbidden')

        if not os.path.exists(path):
            return self.send_error(404, 'File not found')

        self.send_response(200)
        self.send_header("Content-type", self.extensions[ext])
        self.end_headers()

        return path

    def translate_path(self, path):
        """Translate URL to local file system."""
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = os.path.normpath(urllib.unquote(path))
        path = os.path.join(self.wpath, *path.split('/'))

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
