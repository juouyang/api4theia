#!venv/bin/python
from app import create_app
from app.docker import sync_containers_status
from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher
from cheroot.ssl.builtin import BuiltinSSLAdapter

if __name__ == '__main__':
    app = create_app('default')
    sync_containers_status()
    d = WSGIPathInfoDispatcher({'/': app})
    server = WSGIServer(('0.0.0.0', app.config['API_PORT']), d)
    server.ssl_adapter =  BuiltinSSLAdapter(app.config['CRT_FILE'], app.config['KEY_FILE'], None)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()