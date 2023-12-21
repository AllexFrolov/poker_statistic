-- Словари
CREATE TABLE IF NOT EXISTS card_ranks
(
 rank_id  SERIAL PRIMARY KEY,
 "rank"    char(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS card_suits
(
 suit_id  SERIAL PRIMARY KEY,
 suit    char(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS stages
(
 stage_id  SERIAL PRIMARY KEY,
 stage    char(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS actions
(
 action_id  SERIAL PRIMARY KEY,
 "action"    char(15) NOT NULL
);

CREATE TABLE IF NOT EXISTS positions
(
 position_id SERIAL PRIMARY KEY,
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

-- Заполнение словарей

INSERT INTO card_ranks (rank) VALUES
   ('2'),
   ('3'),
   ('4'),
   ('5'),
   ('6'),
   ('7'),
   ('8'),
   ('9'),
   ('T'),
   ('J'),
   ('Q'),
   ('K'),
   ('A');

INSERT INTO card_suits (suit) VALUES
   ('c'),
   ('d'),
   ('h'),
   ('s');

INSERT INTO stages (stage) VALUES
   ('preflop'),
   ('flop'),
   ('turn'),
   ('river'),
   ('showdown');

INSERT INTO actions ("action") VALUES
   ('small blind'),
   ('big blind'),
   ('folds'),
   ('checks'),
   ('calls'),
   ('bets'),
   ('raises'),
   ('returned'),
   ('collected');

INSERT INTO positions ("position") VALUES
   ('SB'),
   ('BB'),
   ('UTG'),
   ('MP'),
   ('CO'),
   ('BTN');