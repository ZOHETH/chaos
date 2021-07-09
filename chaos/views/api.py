# pylint: disable=R
import datetime
import logging
from typing import Any

import simplejson as json
from flask import request, Response
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access_api

from chaos import db
from chaos.typing import FlaskResponse
from chaos.models import core as models
from chaos.views.base import api, BaseAraView, handle_api_exception
from chaos.tasks.async_queries import c_hello, run_main

get_time_range_schema = {"type": "string"}


class Api(BaseAraView):
    @api
    @handle_api_exception
    # @has_access_api
    @expose("/hello/", methods=["GET"])
    def hello(self) -> FlaskResponse:
        c_hello.delay()
        return self.json_response('Hello World', 200)

    """Used for storing and retrieving key value pairs"""

    @api
    @expose("/upload/", methods=["POST"])
    def upload(self) -> FlaskResponse:  # pylint: disable=no-self-use
        audio_url = request.form.get('audio_url', None)
        obj = models.LVCSRProcess(
            audio_url=audio_url,
            create_datetime=datetime.datetime.now()
        )
        db.session.add(obj)
        db.session.commit()
        print(obj.id)
        run_main.delay(obj.id)

        return Response({
            'id': obj.id,
            "audio_url": obj.audio_url,
            "begin_datetime": obj.begin_datetime,
            "callback_url": obj.callback_url,
            "create_datetime": obj.create_datetime,
            "status": obj.status,
        }, status=200)