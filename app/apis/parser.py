from core import STATS
from flask_restx import Namespace, Resource, fields

ROUTE = 'postgres'

api = Namespace(ROUTE, description='parsing poker logs')

sl_ext = api.model(
    f'/{ROUTE}/send_log/expect', 
    {'log': fields.String(required=True, description='Hand logs'),
     'update_stats': fields.Boolean(
         default=False,
         required=False,
         description='Update stats after parsing hand')
         }
         )

ps_ext = api.model(
    f'/{ROUTE}/player_stats/expect', 
    {'palyer_name': fields.String(required=True, description='Player Name'),})

ps_resp = api.model(
    f'/{ROUTE}/player_stats/response', {
        'player_id': fields.Integer(),
        'hands': fields.Integer(),
        'pip': fields.Integer(),
        'pfr': fields.Integer(),
        'sees_flop': fields.Integer(),
        'sees_turn': fields.Integer(),
        'sees_river': fields.Integer(),
        'wins_preflop': fields.Integer(),
        'wins_flop': fields.Integer(),
        'wins_turn': fields.Integer(),
        'wins_river': fields.Integer(),
        'wins_showdown': fields.Integer(),
        'wins': fields.Integer(),
        })


@api.route('/send_log')
class SendLogs(Resource):
    @api.doc('post hand logs')
    @api.expect(sl_ext)
    @api.response(201, description='Success')
    def post(self):
        STATS.parse_log(**api.payload)
        return '', 201

@api.route('/reset_tables')
class ResetTables(Resource):
    @api.doc('Drop all create tables')
    @api.response(201, description='Success')
    def post(self):
        STATS.drop_tables()
        STATS.create_tables()
        STATS.reset()
        return '', 201

@api.route('/create_stats')
class CreateStats(Resource):
    @api.doc('Calculate players statistics')
    @api.response(201, description='Success')
    def post(self):
        STATS.create_raw_stats()
        return '', 201

@api.route('/player_stats')
class PlayerStats(Resource):
    @api.doc('Get player statistics')
    @api.expect(ps_ext)
    @api.marshal_with(ps_resp, code=200)
    def get(self):
        player_name = api.payload['palyer_name']
        return STATS.get_player_stats(player_name), 200
