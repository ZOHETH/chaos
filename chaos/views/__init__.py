from flask import current_app, Flask
from werkzeug.local import LocalProxy
from chaos.app import create_app

from chaos.extensions import (
    appbuilder,
    db,

)

app: Flask = current_app
conf = LocalProxy(lambda: current_app.config)
