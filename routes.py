from CTFd.schemas.files import FileSchema
from CTFd.utils.uploads import get_uploader
from flask_restplus import Resource, Namespace

from CTFd.utils.decorators import admins_only
from CTFd.models import db
from .models import JudgeCaseFiles

cases_namespace = Namespace('cases', description='for ICPC plugin')
@cases_namespace.route('/<int:challenge_id>')
@cases_namespace.param('challenge_id', 'challenge ID')
class ProgrammingCases(Resource):
    @admins_only
    def get(self, challenge_id):
        files = JudgeCaseFiles.query.filter_by(challenge_id=challenge_id).all()
        schema = FileSchema(many=True)
        response = schema.dump(files)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self, challenge_id):
        files = request.files.getlist("file")
        objs = []
        for f in files:
            uploader = get_uploader()
            location = uploader.upload(file_obj=f, filename=f.filename)
            file_row = JudgeCaseFiles(
                challenge_id=challenge_id, location=location)
            db.session.add(file_row)
            db.session.commit()
            objs.append(file_row)
        schema = FileSchema(many=True)
        response = schema.dump(objs)
        if response.errors:
            return {"success": False, "errors": response.errorss}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, challenge_id):
        uploader = get_uploader()
        files = JudgeCaseFiles.query.filter_by(challenge_id=challenge_id).all()
        for f in files:
            uploader.delete(f.location)
        JudgeCaseFiles.query.filter_by(challenge_id=challenge_id).delete()
        db.session.commit()
        db.session.close()
