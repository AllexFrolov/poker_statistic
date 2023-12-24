DROP TABLE IF EXISTS player_raw_stats;

CREATE TABLE player_raw_stats AS
SELECT 
    hand_id
    , player_id
    , CASE WHEN BOOL_OR(stage_id = 1 AND action_id BETWEEN 5 AND 7) THEN 1 ELSE 0 END AS pip
    , CASE WHEN BOOL_OR(stage_id = 1 AND action_id BETWEEN 6 AND 7) THEN 1 ELSE 0 END AS pfr
    , CASE WHEN BOOL_OR(stage_id = 2) THEN 1 ELSE 0 END AS flop
    , CASE WHEN BOOL_OR(stage_id = 3) THEN 1 ELSE 0 END AS turn
    , CASE WHEN BOOL_OR(stage_id = 4) THEN 1 ELSE 0 END AS river
    , CASE WHEN BOOL_OR(stage_id = 1 AND action_id = 9) THEN 1 ELSE 0 END AS win_preflop
    , CASE WHEN BOOL_OR(stage_id = 2 AND action_id = 9) THEN 1 ELSE 0 END AS win_flop
    , CASE WHEN BOOL_OR(stage_id = 3 AND action_id = 9) THEN 1 ELSE 0 END AS win_turn
    , CASE WHEN BOOL_OR(stage_id = 4 AND action_id = 9) THEN 1 ELSE 0 END AS win_river
    , CASE WHEN BOOL_OR(stage_id = 5 AND action_id = 9) THEN 1 ELSE 0 END AS win_showdown
FROM hand_steps
GROUP BY 1, 2
;

CREATE INDEX idx_hand_id_player_id ON player_raw_stats (hand_id, player_id);