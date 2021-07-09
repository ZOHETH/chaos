import dataclasses  # pylint: disable=wrong-import-order
import simplejson as json
import functools
import logging
import traceback
from typing import Any, Callable, cast, Dict, List, Optional, TYPE_CHECKING, Union

from flask_appbuilder import BaseView, Model, ModelView
from chaos.typing import FlaskResponse
from flask import Response, g

from chaos import (
    conf,
)
from chaos.errors import ChaosError
from chaos.utils import core as utils

from .utils import bootstrap_user_data

logger = logging.getLogger(__name__)


def get_error_msg() -> str:
    if conf.get("SHOW_STACKTRACE"):
        error_msg = traceback.format_exc()
    else:
        error_msg = "FATAL ERROR \n"
        error_msg += (
            "Stacktrace is hidden. Change the SHOW_STACKTRACE "
            "configuration setting to enable it"
        )
    return error_msg


def json_error_response(
        msg: Optional[str] = None,
        status: int = 500,
        payload: Optional[Dict[str, Any]] = None,
        link: Optional[str] = None,
) -> FlaskResponse:
    if not payload:
        payload = {"error": "{}".format(msg)}
    if link:
        payload["link"] = link

    return Response(
        json.dumps(payload, ignore_nan=True),
        status=status,
        mimetype="application/json",
    )


def json_errors_response(
        errors: List[ChaosError],
        status: int = 500,
        payload: Optional[Dict[str, Any]] = None,
) -> FlaskResponse:
    if not payload:
        payload = {}

    payload["errors"] = [dataclasses.asdict(error) for error in errors]
    return Response(
        json.dumps(payload, ignore_nan=True),
        status=status,
        mimetype="application/json; charset=utf-8",
    )


def api(f: Callable[..., FlaskResponse]) -> Callable[..., FlaskResponse]:
    """
    A decorator to label an endpoint as an API. Catches uncaught exceptions and
    return the response in the JSON format
    """

    def wraps(self: "BaseChaosView", *args: Any, **kwargs: Any) -> FlaskResponse:
        try:
            return f(self, *args, **kwargs)
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(ex)
            return json_error_response(get_error_msg())

    return functools.update_wrapper(wraps, f)


def handle_api_exception(
        f: Callable[..., FlaskResponse]
) -> Callable[..., FlaskResponse]:
    """
    A decorator to catch Chaos exceptions. Use it after the @api decorator above
    so Chaos exception handler is triggered before the handler for generic
    exceptions.
    """

    def wraps(self: "BaseChaosView", *args: Any, **kwargs: Any) -> FlaskResponse:
        try:
            return f(self, *args, **kwargs)

        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(ex)
            return json_error_response(utils.error_msg_from_exception(ex))

    return functools.update_wrapper(wraps, f)


class BaseChaosView(BaseView):
    @staticmethod
    def json_response(
            obj: Any, status: int = 200
    ) -> FlaskResponse:  # pylint: disable=no-self-use
        return Response(
            json.dumps(obj, ignore_nan=True),
            status=status,
            mimetype="application/json",
        )


class ChaosModelView(ModelView):
    page_size = 100

    def render_app_template(self) -> FlaskResponse:
        payload = {
            "user": bootstrap_user_data(g.user, include_perms=True),
        }
        return self.render_template(
            "superset/spa.html",
            entry="spa",
            bootstrap_data=json.dumps(
                payload
            ),
        )