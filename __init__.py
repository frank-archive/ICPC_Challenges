from flask import render_template_string

from CTFd.api import CTFd_API_v1
from CTFd.models import Submissions
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.utils.decorators import admins_only
from .api import submission_list, query_details
from .models import *
from .routes import cases_namespace

submission_template = '''
<html>
username: {{ user }}<br>
language: {{ lang }}<br>
<code>
{{code}}
</code>
additional info:<br>
{{additional}}
</html>
'''


def load(app):
    CTFd_API_v1.add_namespace(cases_namespace, '/cases')

    @app.route('/submission')
    @admins_only
    def list_submission():
        return json.dumps(submission_list())

    @app.route('/submission/<sub_id>')
    @admins_only
    def get_submission(sub_id):
        username = Submissions.query.filter_by(provided=sub_id).first().user_id
        res = api.query_details(sub_id)['content']
        return render_template_string(
            submission_template,
            user=username,
            code=res['code'],
            lang=res['lang'],
            additional=res['result']
        )

    app.db.create_all()
    CHALLENGE_CLASSES["icpc_dynamic"] = DynICPCChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/CTFd_ICPC_Challenges/assets/"
    )
