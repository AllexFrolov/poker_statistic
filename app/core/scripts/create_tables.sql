-- Словари
CREATE TABLE IF NOT EXISTS card_ranks
(
 rank_id  INT PRIMARY KEY,
 "rank"    char(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS card_suits
(
 suit_id  INT PRIMARY KEY,
 suit    char(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS stages
(
 stage_id  INT PRIMARY KEY,
 stage    char(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS actions
(
 action_id  INT PRIMARY KEY,
 "action"    char(15) NOT NULL
);

CREATE TABLE IF NOT EXISTS positions
(
 position_id INT PRIMARY KEY,
 position    char(3) NOT NULL
);

CREATE TABLE IF NOT EXISTS players
(
    player_id SERIAL PRIMARY KEY,
    player    CHAR(50) NOT NULL
);

-- Главные таблицы

CREATE TABLE IF NOT EXISTS hands
(
    hand_id    INT PRIMARY KEY,
    table_name CHAR(50) NOT NULL,
    sb int NOT NULL,
    bb int NOT NULL,
    ante int
);

CREATE TABLE IF NOT EXISTS player_hand
(
    hand_id    INT REFERENCES hands(hand_id),
    player_id INT REFERENCES players(player_id),
    position_id INT REFERENCES positions(position_id),
    chips int NOT NULL,
    CONSTRAINT uq_player_hand_info UNIQUE (hand_id, player_id)
);

-- Зависимые таблицы

CREATE TABLE IF NOT EXISTS player_start_hand
(
    hand_id    INT REFERENCES hands(hand_id),
    player_id INT REFERENCES players(player_id),
    cards integer[2][2] NOT NULL,
    CONSTRAINT uq_player_start_hand_info UNIQUE (hand_id, player_id)
);

CREATE TABLE IF NOT EXISTS hand_steps
(
    hand_id    INT REFERENCES hands(hand_id),
    stage_id INT REFERENCES stages(stage_id),
    step INT NOT NULL,
    player_id INT REFERENCES players(player_id),
    action_id INT REFERENCES actions(action_id),
    chips int,
    CONSTRAINT uq_hand_steps_info UNIQUE (hand_id, stage_id, step)
);

CREATE TABLE IF NOT EXISTS hand_stage_cards
(
    hand_id    INT REFERENCES hands(hand_id),
    stage_id INT REFERENCES stages(stage_id),
    cards integer[3][2],
    CONSTRAINT uq_hand_stage_cards_info UNIQUE (hand_id, stage_id)
);

-- Процедуры

CREATE OR REPLACE FUNCTION calculate_statistics(hand_steps_table hand_steps[])
RETURNS TABLE (
    hand_id INT,
    player_id INT,
    pip INT,
    pfr INT,
    flop INT,
    turn INT,
    river INT,
    win_preflop INT,
    win_flop INT,
    win_turn INT,
    win_river INT,
    win_showdown INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        hand_id,
        player_id,
        CASE WHEN BOOL_OR(stage_id = 1 AND action_id BETWEEN 5 AND 7) THEN 1 ELSE 0 END AS pip,
        CASE WHEN BOOL_OR(stage_id = 1 AND action_id BETWEEN 6 AND 7) THEN 1 ELSE 0 END AS pfr,
        CASE WHEN BOOL_OR(stage_id = 2) THEN 1 ELSE 0 END AS flop,
        CASE WHEN BOOL_OR(stage_id = 3) THEN 1 ELSE 0 END AS turn,
        CASE WHEN BOOL_OR(stage_id = 4) THEN 1 ELSE 0 END AS river,
        CASE WHEN BOOL_OR(stage_id = 1 AND action_id = 9) THEN 1 ELSE 0 END AS win_preflop,
        CASE WHEN BOOL_OR(stage_id = 2 AND action_id = 9) THEN 1 ELSE 0 END AS win_flop,
        CASE WHEN BOOL_OR(stage_id = 3 AND action_id = 9) THEN 1 ELSE 0 END AS win_turn,
        CASE WHEN BOOL_OR(stage_id = 4 AND action_id = 9) THEN 1 ELSE 0 END AS win_river,
        CASE WHEN BOOL_OR(stage_id = 5 AND action_id = 9) THEN 1 ELSE 0 END AS win_showdown
    FROM unnest(hand_steps_table) AS hand_steps
    GROUP BY 1, 2;
END;
$$ LANGUAGE plpgsql;

-- Заполнение словарей

INSERT INTO card_ranks (rank_id, rank) VALUES
   (1, '2'),
   (2, '3'),
   (3, '4'),
   (4, '5'),
   (5, '6'),
   (6, '7'),
   (7, '8'),
   (8, '9'),
   (9, 'T'),
   (10, 'J'),
   (11, 'Q'),
   (12, 'K'),
   (13, 'A')
ON CONFLICT (rank_id) DO NOTHING;

INSERT INTO card_suits (suit_id, suit) VALUES
   (1, 'c'),
   (2, 'd'),
   (3, 'h'),
   (4, 's')
ON CONFLICT (suit_id) DO NOTHING;

INSERT INTO stages (stage_id, stage) VALUES
   (1, 'preflop'),
   (2, 'flop'),
   (3, 'turn'),
   (4, 'river'),
   (5, 'showdown')
ON CONFLICT (stage_id) DO NOTHING;

INSERT INTO actions (action_id, "action") VALUES
   (1, 'small blind'),
   (2, 'big blind'),
   (3, 'folds'),
   (4, 'checks'),
   (5, 'calls'),
   (6, 'bets'),
   (7, 'raises'),
   (8, 'returned'),
   (9, 'collected')
ON CONFLICT (action_id) DO NOTHING;

INSERT INTO positions (position_id, "position") VALUES
   (1, 'SB'),
   (2, 'BB'),
   (3, 'UTG'),
   (4, 'MP'),
   (5, 'CO'),
   (6, 'BTN')
ON CONFLICT (position_id) DO NOTHING;