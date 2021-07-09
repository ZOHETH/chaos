import os
import logging
from typing import Any,Callable,Dict

from flask import Flask, redirect
from flask_appbuilder import expose, IndexView

from chaos.extensions import (
    APP_DIR,
    appbuilder,
    db,
    migrate
)

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(__name__)

    try:
        app.config.from_object("chaos.config")
        app_initializer=

class AppInitializer:
    def __init__(self, app: Flask) -> None:
        super().__init__()

        self.flask_app = app
        self.config = app.config
        self.manifest: Dict[Any, Any] = {}

    def init_views():
        from chaos.views.api import Api
        #
        # Setup API views
        #
        appbuilder.add_api(Api)

        from ara.views.demo import DemoModelView
        appbuilder.add_view(
            DemoModelView,
            "List Contacts",
            icon="fa-envelope",
            category="Contacts"
        )

    def init_app_in_ctx(self) -> None:
        """
        Runs init logic in the context of the app
        """
        self.configure_fab()
        self.init_views()

    def init_app(self) -> None:
        """
        Main entry point which will delegate to other methods in
        order to fully init the app
        """
        # Configuration of logging must be done first to apply the formatter properly
        self.configure_logging()
        self.setup_db()
        self.register_blueprints()

        with self.flask_app.app_context():  # type: ignore
            self.init_app_in_ctx()


    def configure_fab(self) -> None:
        if self.config["SILENCE_FAB"]:
            logging.getLogger("flask_appbuilder").setLevel(logging.ERROR)

        appbuilder.init_app(self.flask_app, None)

    def configure_logging(self) -> None:
        self.config["LOGGING_CONFIGURATOR"].configure_logging(
            self.config, self.flask_app.debug
        )

    def setup_db(self) -> None:
        db.init_app(self.flask_app)

        migrate.init_app(self.flask_app, db=db, directory=APP_DIR + "/migrations")

    def register_blueprints(self) -> None:
        for bp in self.config["BLUEPRINTS"]:
            try:
                logger.info("Registering blueprint: %s", bp.name)
                self.flask_app.register_blueprint(bp)
            except Exception:  # pylint: disable=broad-except
                logger.exception("blueprint registration failed")