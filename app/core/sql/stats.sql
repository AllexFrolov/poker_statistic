DROP TABLE IF EXISTS player_stats;

CREATE TABLE player_stats AS
WITH player_stages AS (
    SELECT 
        hand_id
        , player_id
        , CASE WHEN BOOL_OR(stage_id = 1 and action_id BETWEEN 5 AND 7) THEN 1 ELSE 0 END AS pip
        , CASE WHEN BOOL_OR(stage_id = 1 and action_id BETWEEN 6 AND 7) THEN 1 ELSE 0 END AS pfr
        , CASE WHEN BOOL_OR(stage_id = 2) THEN 1 ELSE 0 END                               AS flop
        , CASE WHEN BOOL_OR(stage_id = 3) THEN 1 ELSE 0 END                               AS turn
        , CASE WHEN BOOL_OR(stage_id = 4) THEN 1 ELSE 0 END                               AS river
        , CASE WHEN BOOL_OR(stage_id = 1 and action_id = 9) THEN 1 ELSE 0 END             AS win_preflop
        , CASE WHEN BOOL_OR(stage_id = 2 and action_id = 9) THEN 1 ELSE 0 END             AS win_flop
        , CASE WHEN BOOL_OR(stage_id = 3 and action_id = 9) THEN 1 ELSE 0 END             AS win_turn
        , CASE WHEN BOOL_OR(stage_id = 4 and action_id = 9) THEN 1 ELSE 0 END             AS win_river
        , CASE WHEN BOOL_OR(stage_id = 5 and action_id = 9) THEN 1 ELSE 0 END             AS win_showdown
    FROM hand_steps
    GROUP BY 1, 2
),
grouped_player_stages AS (
    SELECT 
        player_id
        , COUNT(*)          AS hands
        , SUM(pip)          AS pip
        , SUM(pfr)          AS pfr
        , SUM(flop)         AS sees_flop
        , SUM(turn)         AS sees_turn
        , SUM(river)        AS sees_river
        , SUM(win_preflop)  AS wins_preflop
        , SUM(win_flop)     AS wins_flop
        , SUM(win_turn)     AS wins_turn
        , SUM(win_river)    AS wins_river
        , SUM(win_showdown) AS wins_showdown
    FROM player_stages
    GROUP BY 1
)
SELECT ps.*
    , wins_preflop + wins_flop + wins_turn + wins_river + wins_showdown AS wins
FROM grouped_player_stages ps
;

CREATE INDEX idx_player_id ON player_stats (player_id);