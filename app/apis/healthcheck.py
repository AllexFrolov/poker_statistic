from core import STATS, Statistic
from flask_restx import Namespace, Resource, fields

ROUTE = 'healthcheck'

api = Namespace(ROUTE)

healthcheck = api.model(f'/{ROUTE}', {
    'status': fields.Boolean(readonly=True)
})

@api.route('/')
class HealthCheck(Resource):
    @api.marshal_with(healthcheck)
    def get(self):
        if isinstance(STATS, Statistic):
            return {'status': True}
        return {'status': False}
