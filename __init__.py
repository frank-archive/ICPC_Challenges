from flask import request

from CTFd.api import CTFd_API_v1
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from .models import *
from .routes import cases_namespace


def load(app):
    CTFd_API_v1.add_namespace(cases_namespace, '/cases')

    app.db.create_all()
    CHALLENGE_CLASSES["programming"] = ICPCChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/programming_challenges/assets/"
    )
