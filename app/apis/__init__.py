from flask_restx import Api

from .healthcheck import api as hc
from .parser import api as pl


api = Api(
    title='Poker API',
    version='1.0',
    description='',
    )

api.add_namespace(hc)
api.add_namespace(pl)
