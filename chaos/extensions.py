import celery
import os
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_mongoengine import MongoEngine

APP_DIR = os.path.dirname(__file__)
appbuilder = AppBuilder(update_perms=False, security_manager_class=SecurityManager)

db = MongoEngine()
