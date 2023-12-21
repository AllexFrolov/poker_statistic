from core import STATS
from flask_restx import Namespace, Resource, fields

api = Namespace('parser', description='parsing poker logs')

pl_resp = api.model(
    '/parse_logs/post response',
    {'status': fields.String()})

pl_ext = api.model(
    '/parse_logs/post expect', 
    {'log': fields.String(required=True, description='Hand logs'),})


@api.route('/parse_logs')
class ParseLogs(Resource):
    @api.doc('post hand logs')
    @api.expect(pl_ext)
    @api.marshal_with(pl_resp, code=201)
    def post(self):
        log = api.payload['log']
        STATS.parse_log(log)
        return {'status': 'success'}, 201
