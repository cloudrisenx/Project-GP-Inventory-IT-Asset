class ReverseProxied(object):
    """Middleware untuk memastikan URL di-generate dengan subpath (/inventory) saat di Nginx."""
    def __init__(self, app, script_name):
        self.app = app
        self.script_name = script_name
        
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.script_name
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith(self.script_name):
            environ['PATH_INFO'] = path_info[len(self.script_name):]
        return self.app(environ, start_response)