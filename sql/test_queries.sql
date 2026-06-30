-- Test 1: Verify player counts grouped by league and position
SELECT league_name, position, COUNT(*) as total_players 
FROM players 
GROUP BY league_name, position;

-- Test 2: Find top 5 midfielders based on high interceptions and average distance covered
SELECT p.name, p.current_club, s.season, s.interceptions, s.avg_km_per_match
FROM players p
JOIN outfield_stats s ON p.player_id = s.player_id
WHERE p.position = 'Midfielder' AND s.season = '2025/2026'
ORDER BY s.interceptions DESC, s.avg_km_per_match DESC
LIMIT 5;