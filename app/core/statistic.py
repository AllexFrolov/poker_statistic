# pylint: disable=C0114:missing-module-docstring
import re
from pathlib import Path
import psycopg2

class Statistic:
    """
    A class for parsing and storing poker game statistics in a PostgreSQL database.

    Attributes:
        connection (psycopg2.extensions.connection): The connection to the PostgreSQL database.
        cursor (psycopg2.extensions.cursor): The database cursor.
        table_name (str): The name of the poker table.
        positions (dict): A dictionary mapping position names to their corresponding IDs in the database.
        actions (dict): A dictionary mapping poker actions to their corresponding IDs in the database.
        card_ranks (dict): A dictionary mapping card ranks to their corresponding IDs in the database.
        card_suits (dict): A dictionary mapping card suits to their corresponding IDs in the database.
        stages (dict): A dictionary mapping poker game stages to their corresponding IDs in the database.
        players (dict): A dictionary to cache player IDs for efficient database queries.
    """
    def __init__(self, db_params: dict) -> None:
        """
        Initialize a Statistic object.

        Args:
            db_params (dict): A dictionary containing database connection parameters.
            table_name (str): The name of the poker table.
        """
        self.scripts_paths = Path(__file__).parent.joinpath('sql')
        self.connection = psycopg2.connect(**db_params)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.reset()

    def reset(self):
        """
            reset dictionaries
        """
        self.positions = self.get_table_dict('POSITIONS')
        self.actions = self.get_table_dict('ACTIONS')
        self.card_ranks = self.get_table_dict('CARD_RANKS')
        self.card_suits = self.get_table_dict('CARD_SUITS')
        self.stages = self.get_table_dict('STAGES')
        self.players = {}

    def get_table_dict(self, table_name: str) -> dict:
        """
        Retrieve a dictionary mapping values from a database table.

        Args:
            table_name (str): The name of the database table.

        Returns:
            dict: A dictionary mapping values from the specified database table.
        """
        self.cursor.execute(f'SELECT * FROM {table_name}')
        table_dict = {}
        for row in self.cursor.fetchall():
            table_dict[row[1].strip()] = row[0]
        return table_dict

    @staticmethod
    def extract_btn_seat(table_description):
        """
        Extract the button seat number from a table description.

        Args:
            table_description (str): The description of the poker table.

        Returns:
            int: The button seat number.
        """
        match = re.search(r"Seat #(\d+)", table_description)
        return int(match.group(1))

    def parse_player_hand(self, init_part: str, hand_id: int):
        """
        Parse and store information about players' hands.

        Args:
            init_part (str): The initial part of the game log.
            hand_id (int): The ID of the current hand.
        """
        player_pattern = re.compile(r"Seat (\d+): (\w+) \(\$([\d.]+) in chips\)")
        players = player_pattern.findall(init_part)
        bnt_seat = self.extract_btn_seat(init_part) - 1

        num_players = len(players)
        positions = {
            6: {1: 'SB', 2: 'BB', 3: 'UTG', 4: 'MP', 5: 'CO', 0: 'BTN'},
            5: {1: 'SB', 2: 'BB', 3: 'MP', 4: 'CO', 0: 'BTN'},
            4: {1: 'SB', 2: 'BB', 3: 'CO', 0: 'BTN'},
            3: {1: 'SB', 2: 'BB', 0: 'BTN'},
            }
        data = []
        for i, seat in enumerate(range(bnt_seat, bnt_seat + num_players)):
            current_index = seat % num_players
            _, player, chips = players[current_index]
            data.append({
                'player_id': self.get_player_id(player),
                'position_id': self.positions[positions[num_players][i]],
                'chips': int(float(chips) * 100),
                'hand_id': hand_id
                })

        for row in data:
            self.cursor.execute(
                "INSERT INTO player_hand (player_id, hand_id, position_id, chips) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (row['player_id'], row['hand_id'], row['position_id'], row['chips'])
            )

    def parse_player_start_hand(self, preflop_part: str, hand_id: int):
        """
        Parse and store information about players' starting hands.

        Args:
            preflop_part (str): The preflop part of the game log.
            hand_id (int): The ID of the current hand.
        """
        card_pattern = re.compile(r"Dealt to (\w+): \[([2-9TJQKAcdhs]{2}), ([2-9TJQKAcdhs]{2})\]")

        data = []
        for match in card_pattern.finditer(preflop_part):
            player_name = match.group(1)
            card1 = match.group(2)
            card2 = match.group(3)
            data.append({
                'player_id': self.get_player_id(player_name),
                'hand_id': hand_id,
                'cards': [[self.card_ranks[card1[0]], self.card_suits[card1[1]]],
                          [self.card_ranks[card2[0]], self.card_suits[card2[1]]]]
            })
        for row in data:
            self.cursor.execute(
                "INSERT INTO player_start_hand (player_id, hand_id, cards) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (row['player_id'], row['hand_id'], row['cards'])
            )

    def parse_actions(self, text, stage_id: int, hand_id: int):
        """
        Parse and store information about player actions during a game stage.

        Args:
            text (str): The text containing player actions.
            stage_id (int): The ID of the current game stage.
            hand_id (int): The ID of the current hand.

        Returns:
            list: A list of dictionaries containing parsed action information.
        """
        patterns = (
            r'(\n|^)(?P<player>\w+): (?:posts )?(?P<action>small blind|big blind|folds|calls|bets|checks|raises)(?: \$[\d.]+ to)?(?: \$(?P<amount>[\d.]+))?',
            r'(\n|^)Uncalled bet \(\$(?P<amount>[\d.]+)\) (?P<action>\w+) to (?P<player>\w+)',
            r'(\n|^)(?P<player>\w+) (?P<action>\w+) \$(?P<amount>[\d.]+)')

        data = []
        step = 0
        for pattern in patterns:
            action_pattern = re.compile(pattern)
            for match in action_pattern.finditer(text):
                player = match.group('player')
                action_type = match.group('action')
                chips = int(float(match.group('amount')) * 100) if match.group('amount') else None
                if chips and action_type not in ['returned', 'collected']:
                    chips = -chips

                data.append({
                    'player_id': self.get_player_id(player),
                    'action_id': self.actions[action_type],
                    'hand_id': hand_id,
                    'step': step,
                    'stage_id': stage_id,
                    'chips': chips,
                })
                step += 1

        for row in data:
            self.cursor.execute(
                "INSERT INTO hand_steps (player_id, hand_id, step, stage_id, action_id, chips) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (row['player_id'], row['hand_id'], row['step'], row['stage_id'], row['action_id'], row['chips'])
            )

        return data

    def get_player_id(self, pl_name: str) -> int:
        """
        Retrieve or create a player ID.

        Args:
            pl_name (str): The name of the player.

        Returns:
            int: The player ID.
        """
        player_id = self.players.get(pl_name)
        if player_id:
            return player_id

        self.cursor.execute("SELECT player_id FROM players WHERE player = %s", (pl_name,))
        result = self.cursor.fetchone()
        if result:
            player_id = result[0]
        else:
            self.cursor.execute("INSERT INTO players (player) VALUES (%s) RETURNING player_id", (pl_name,))
            player_id = self.cursor.fetchone()[0]
        self.players[pl_name] = player_id
        return player_id

    @staticmethod
    def split_and_create_dict(text: str) -> dict:
        """
        Split the game log into different stages and create a dictionary.

        Args:
            text (str): The game log text.

        Returns:
            dict: A dictionary containing game log stages.
        """
        stages = re.split(r'\*{3}\s(?:FLOP|TURN|RIVER|SHOW\sDOWN)\s\*{3}', text)
        stages_dict = {}

        for i, key in enumerate(['preflop', 'flop', 'turn', 'river', 'showdown']):
            stages_dict[key] = stages[i].strip() if i < len(stages) else ''

        return stages_dict

    def parse_hands(self, text: str) -> dict:
        """
        Parse and store information about the current hand.

        Args:
            text (str): The text containing hand information.

        Returns:
            dict: A dictionary containing parsed hand information.
        """
        pattern_1 = r"Hand #(?P<hand_id>\d+) Hold'em No Limit \(\$(?P<sb>[\d.]+)\/\$(?P<bb>[\d.]+) USD\).*\nTable '(?P<table_name>\w+)'"
        data = {}
        comp = re.compile(pattern_1)
        for match in comp.finditer(text):
            data.update({
                'hand_id': int(match.group('hand_id')),
                'table_name': match.group('table_name'),
                'sb':  int(float(match.group('sb')) * 100),
                'bb': int(float(match.group('bb')) * 100),
            })
        self.cursor.execute(
            "INSERT INTO hands (hand_id, table_name, sb, bb) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (data['hand_id'], data['table_name'], data['sb'], data['bb'])
        )

        return data

    def parse_log(self, log: str):
        """
        Parse and store information from the entire game log.

        Args:
            logs (str): The entire game log text.
        """
        stages = self.split_and_create_dict(log)
        hand_id = self.parse_hands(stages['preflop'])['hand_id']
        self.parse_player_hand(stages['preflop'], hand_id)
        self.parse_player_start_hand(stages['preflop'], hand_id)
        for stage_name, stage_logs in stages.items():
            self.parse_actions(stage_logs, self.stages[stage_name], hand_id)
        self.commit()


    def commit(self):
        """Commit chanches to database"""
        self.connection.commit()

    def create_stats(self):
        """create player stats"""
        drop_tables = self.scripts_paths.joinpath('stats.sql').read_text()
        self.cursor.execute(drop_tables)
        self.commit()


    # def parse_log_files(self):
    #     """parsing log files in logs_path"""
    #     for file_path in Path(self.logs_path).glob('*.txt'):
    #         if 'test' not in file_path.name:
    #             logs = file_path.read_text()
    #             logs = logs.split('PokerStars')
    #             for log in logs[1:]:
    #                 self.parse_log(log)
    #             self.commit()
    #     self.create_stats()

    def drop_tables(self):
        """drop all tables"""
        drop_tables = self.scripts_paths.joinpath('drop_tables.sql').read_text()
        self.cursor.execute(drop_tables)
        self.commit()

    def create_tables(self):
        """create tables"""
        create_tables = self.scripts_paths.joinpath('create_tables.sql').read_text()
        self.cursor.execute(create_tables)
        self.commit()

    def close(self):
        """Close the database connection."""
        self.connection.close()

    def get_player_stats(self, pl_name: str) -> dict:
        player_id = self.get_player_id(pl_name=pl_name)
        pl_stats = self.scripts_paths.joinpath('get_player_stats.sql').read_text()
        pl_stats = pl_stats % (player_id)
        self.cursor.execute(pl_stats)
        result = self.cursor.fetchone()
        if result:
            return dict(zip([desc[0] for desc in self.cursor.description], result))
        return {}
