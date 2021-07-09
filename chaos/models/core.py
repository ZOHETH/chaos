import json
import logging
from typing import Any, Dict, List

from mongoengine import Document
from mongoengine import DateTimeField,StringField,ReferenceField,DictField,ListField

from chaos import app

config = app.config
logger = logging.getLogger(__name__)


class Customer(Model):
    __tablename__="customer"


class Conversation(Model):
    __tablename__ = "conversation"
