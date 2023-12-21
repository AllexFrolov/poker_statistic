import os
import time
from flask import Flask
from flask_restx import Api, Resource, fields

from src import (
    Statistic
    )

DB_PARAMS = {
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT'],
    'user': os.environ['POSTGRES_USER'],
    'password': os.environ['POSTGRES_PASSWORD'],
    'database': os.environ['POSTGRES_DB']
}

def wait_for_it(db_params: dict) -> Statistic:
    """wait connect to db"""
    exeption = None
    for _ in range(10):
        try:
            stats = Statistic(db_params)
            return stats
        except Exception as e:
            time.sleep(2)
            exeption = e

    raise ConnectionError(exeption)


app = Flask(__name__)
api = Api(
    app,
    title='Иди нахуй',
    description='Иди нахуй API',
    )
hc = api.namespace('healthcheck')
pl = api.namespace('parsing', description='parsing poker logs')

pl_resp = api.model(
    '/parse_logs/post response',
    {'status': fields.String(description='Статус')})

pl_ext = api.model(
    '/parse_logs/post expect', 
    {'log': fields.String(required=True, description='Логи раздачи'),})

healthcheck = api.model('/healthcheck', {
    'status': fields.Boolean(readonly=True)
})

@hc.route('/')
class HealthCheck(Resource):
    @pl.marshal_with(healthcheck)
    def get(self):
        if isinstance(STATS, Statistic):
            return {'status': True}
        return {'status': False}

@pl.route('/parse_logs')
class ParseLogs(Resource):
    @pl.doc('post hand logs')
    @pl.expect(pl_ext)
    @pl.marshal_with(pl_resp, code=201)
    def post(self):
        log = api.payload['log']
        STATS.parse_log(log)
        return {'status': 'success'}, 201

STATS = wait_for_it(DB_PARAMS)
