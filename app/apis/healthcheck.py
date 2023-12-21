from core import STATS, Statistic
from flask_restx import Namespace, Resource, fields

api = Namespace('healthcheck')

healthcheck = api.model('/healthcheck', {
    'status': fields.Boolean(readonly=True)
})

@api.route('/')
class HealthCheck(Resource):
    @api.marshal_with(healthcheck)
    def get(self):
        if isinstance(STATS, Statistic):
            return {'status': True}
        return {'status': False}
