# This file is used by the webserver on staging/prod to allow gunicorn to run the app behind a reverse proxy (nginx)

from pkg import osfflask

app = osfflask.create_app()