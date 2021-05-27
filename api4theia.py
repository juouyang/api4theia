#!venv/bin/python
from app import create_app
from app.docker import sync_containers_status
from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher
from cheroot.ssl.builtin import BuiltinSSLAdapter
import os

if __name__ == '__main__':
    flask_config = os.getenv('FLASK_CONFIG') or 'default'
    app = create_app(flask_config)
    sync_containers_status()

    if (flask_config == 'prod'):
        d = WSGIPathInfoDispatcher({'/': app})
        server = WSGIServer(('0.0.0.0', app.config['API_PORT']), d)
        server.ssl_adapter =  BuiltinSSLAdapter(app.config['CRT_FILE'], app.config['KEY_FILE'], None)
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
    else:
        context = (app.config['CRT_FILE'], app.config['KEY_FILE'])
        app.run(host='0.0.0.0', port=app.config['API_PORT'], debug=app.config['DEBUG'], ssl_context=context)