from flask_restx import Api

from .healthcheck import api as hc
from .parser import api as pl


api = Api(
    title='Иди нахуй',
    description='Иди нахуй API',
    )

api.add_namespace(hc)
api.add_namespace(pl)
