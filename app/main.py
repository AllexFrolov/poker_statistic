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
    exeption = None
    for _ in round(10):
        try:
            return Statistic(db_params)
        except ConnectionError as e:
            time.sleep(5)
            exeption = e

    raise ConnectionError(exeption)

app = Flask(__name__)
api = Api(app, title='Иди нахуй', description='Иди нахуй API')
ns = api.namespace('parsing', description='parsing poker logs')

todo = api.model('/parse_logs/post response', {
    'status': fields.Integer(default=200, description='Статус'),
})


@ns.route('/parse_logs/<log>')
@ns.doc(params={'log': 'Лог ондой раздачи Сука'})
class ParseLogs(Resource):
    @ns.doc('post hand logs')
    @ns.marshal_with(todo)
    def post(self, log):
        return 200
