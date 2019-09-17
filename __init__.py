from CTFd.api import CTFd_API_v1
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.utils.decorators import admins_only
from .api import submission_list, query_details
from .models import *
from .routes import cases_namespace


def load(app):
    CTFd_API_v1.add_namespace(cases_namespace, '/cases')

    @app.route('submission')
    @admins_only
    def list_submission():
        return json.dumps(submission_list())

    @app.route('submission/<str:sub_id>')
    @admins_only
    def get_submission(sub_id):
        return json.dumps(query_details(sub_id))

    app.db.create_all()
    CHALLENGE_CLASSES["icpc_dynamic"] = DynICPCChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/CTFd-ICPC-challenges/assets/"
    )
