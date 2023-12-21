DO $$ 
DECLARE
    tn text;
BEGIN
    FOR tn IN (
        SELECT table_name 
        FROM (
            SELECT table_name,
            SUM(CASE WHEN constraint_type = 'FOREIGN KEY' THEN 1 ELSE 0 END
            ) as num_dependencies
FROM information_schema.table_constraints
WHERE constraint_schema = 'public'
GROUP BY table_name
ORDER BY num_dependencies DESC) as t) 
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || tn || ';';
    END LOOP;
END $$;

DROP TABLE IF EXISTS player_stats;