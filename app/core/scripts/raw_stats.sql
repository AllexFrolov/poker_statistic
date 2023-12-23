DROP TABLE IF EXISTS player_raw_stats;

CREATE TABLE player_raw_stats AS
SELECT * 
FROM calculate_statistics((SELECT ARRAY(SELECT * FROM hand_steps)))
;

CREATE INDEX idx_hand_id_player_id ON player_raw_stats (hand_id, player_id);