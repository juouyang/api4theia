#!venv/bin/python
from app import create_app
from app.docker import sync_containers_status

app = create_app('default')
sync_containers_status()
context = (app.config['CRT_FILE'], app.config['KEY_FILE'])
app.run(host='0.0.0.0', port=app.config['API_PORT'], debug=app.config['DEBUG'], ssl_context=context)