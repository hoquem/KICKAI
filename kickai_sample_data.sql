-- KICKAI Sample Data
-- Inserts realistic sample data for the BP Hatters team

-- =========================
-- 1. SAMPLE PLAYERS
-- =========================
INSERT INTO players (id, name, phone_number, is_active, team_id) VALUES
(gen_random_uuid(), 'Alex Johnson', '+447123456789', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Ben Smith', '+447123456790', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Charlie Brown', '+447123456791', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'David Wilson', '+447123456792', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Ethan Davis', '+447123456793', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Frank Miller', '+447123456794', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'George Taylor', '+447123456795', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Harry Anderson', '+447123456796', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Ian Thomas', '+447123456797', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Jack Jackson', '+447123456798', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Kevin White', '+447123456799', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Liam Harris', '+447123456800', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Mike Clark', '+447123456801', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Nick Lewis', '+447123456802', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee'),
(gen_random_uuid(), 'Oscar Walker', '+447123456803', TRUE, '0854829d-445c-4138-9fd3-4db562ea46ee');

-- =========================
-- 2. TEAM MEMBERS (with roles) - using player IDs from above
-- =========================
INSERT INTO team_members (team_id, player_id, phone, role, telegram_username, is_active)
SELECT 
    '0854829d-445c-4138-9fd3-4db562ea46ee',
    p.id,
    p.phone_number,
    CASE 
        WHEN p.name = 'Alex Johnson' THEN 'admin'
        WHEN p.name = 'Ben Smith' THEN 'manager'
        WHEN p.name = 'Charlie Brown' THEN 'secretary'
        WHEN p.name = 'David Wilson' THEN 'treasurer'
        WHEN p.name = 'Ethan Davis' THEN 'helper'
        ELSE 'player'
    END,
    CASE 
        WHEN p.name = 'Alex Johnson' THEN 'alex_admin'
        WHEN p.name = 'Ben Smith' THEN 'ben_manager'
        WHEN p.name = 'Charlie Brown' THEN 'charlie_secretary'
        WHEN p.name = 'David Wilson' THEN 'david_treasurer'
        WHEN p.name = 'Ethan Davis' THEN 'ethan_helper'
        WHEN p.name = 'Frank Miller' THEN 'frank_player'
        WHEN p.name = 'George Taylor' THEN 'george_player'
        WHEN p.name = 'Harry Anderson' THEN 'harry_player'
        WHEN p.name = 'Ian Thomas' THEN 'ian_player'
        WHEN p.name = 'Jack Jackson' THEN 'jack_player'
        WHEN p.name = 'Kevin White' THEN 'kevin_player'
        WHEN p.name = 'Liam Harris' THEN 'liam_player'
        WHEN p.name = 'Mike Clark' THEN 'mike_player'
        WHEN p.name = 'Nick Lewis' THEN 'nick_player'
        WHEN p.name = 'Oscar Walker' THEN 'oscar_player'
    END,
    TRUE
FROM players p
WHERE p.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
ON CONFLICT (team_id, phone) DO NOTHING;

-- =========================
-- 3. SAMPLE FIXTURES (next 4 weeks)
-- =========================
INSERT INTO fixtures (id, team_id, opponent, match_date, venue, home_away, status) VALUES
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Red Lions FC', '2024-01-20 14:00:00+00', 'Victoria Park', 'home', 'scheduled'),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Blue Eagles FC', '2024-01-27 15:30:00+00', 'Riverside Stadium', 'away', 'scheduled'),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Green Dragons FC', '2024-02-03 14:00:00+00', 'Victoria Park', 'home', 'scheduled'),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Yellow Tigers FC', '2024-02-10 16:00:00+00', 'Central Arena', 'away', 'scheduled');

-- =========================
-- 4. SAMPLE TASKS
-- =========================
INSERT INTO tasks (id, team_id, name, description, is_active) VALUES
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Wash Kit', 'Wash and dry all team kit after the match', TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Bring Oranges', 'Bring oranges for half-time refreshments', TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Pump Footballs', 'Pump up match balls before the game', TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Bring Equipment Bag', 'Bring the team equipment bag with first aid kit', TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Set Up Goals', 'Help set up and take down goal posts', TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Match Report', 'Write and submit the match report', TRUE);

-- =========================
-- 5. SAMPLE EQUIPMENT
-- =========================
INSERT INTO equipment (id, team_id, name, description, quantity, is_active) VALUES
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'First Aid Kit', 'Complete first aid kit with bandages, ice packs, etc.', 1, TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Match Balls', 'Official match footballs', 3, TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Training Bibs', 'High-visibility training bibs for practice', 12, TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Cones', 'Training cones for drills', 20, TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Goal Posts', 'Portable goal posts for training', 2, TRUE),
(gen_random_uuid(), '0854829d-445c-4138-9fd3-4db562ea46ee', 'Team Kit', 'Complete team kit (home and away)', 15, TRUE);

-- =========================
-- 6. SAMPLE AVAILABILITY (for first fixture)
-- =========================
INSERT INTO availability (team_id, player_id, fixture_id, status, squad_status, has_paid_fees)
SELECT 
    '0854829d-445c-4138-9fd3-4db562ea46ee',
    p.id,
    f.id,
    CASE 
        WHEN p.name IN ('Alex Johnson', 'Ben Smith', 'Charlie Brown', 'David Wilson', 'Ethan Davis') THEN 'Available'
        WHEN p.name IN ('Frank Miller', 'George Taylor', 'Harry Anderson') THEN 'Available'
        WHEN p.name IN ('Ian Thomas', 'Oscar Walker') THEN 'Maybe'
        WHEN p.name IN ('Jack Jackson', 'Liam Harris') THEN 'Unavailable'
        ELSE 'Available'
    END,
    CASE 
        WHEN p.name IN ('Alex Johnson', 'Ben Smith', 'Charlie Brown', 'David Wilson', 'Ethan Davis') THEN 'Starting XI'
        WHEN p.name IN ('Frank Miller', 'George Taylor', 'Harry Anderson') THEN 'Substitute'
        WHEN p.name IN ('Jack Jackson', 'Liam Harris') THEN 'Not Selected'
        ELSE 'Reserve'
    END,
    CASE 
        WHEN p.name IN ('Harry Anderson', 'Kevin White') THEN FALSE
        ELSE TRUE
    END
FROM players p
CROSS JOIN fixtures f
WHERE p.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.opponent = 'Red Lions FC'
ON CONFLICT (player_id, fixture_id) DO NOTHING;

-- =========================
-- 7. SAMPLE TASK ASSIGNMENTS (for first fixture)
-- =========================
INSERT INTO task_assignments (team_id, task_id, player_id, fixture_id)
SELECT 
    '0854829d-445c-4138-9fd3-4db562ea46ee',
    t.id,
    p.id,
    f.id
FROM tasks t
CROSS JOIN players p
CROSS JOIN fixtures f
WHERE t.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND p.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.opponent = 'Red Lions FC'
AND (
    (t.name = 'Wash Kit' AND p.name = 'Charlie Brown') OR
    (t.name = 'Bring Oranges' AND p.name = 'Ethan Davis') OR
    (t.name = 'Pump Footballs' AND p.name = 'George Taylor') OR
    (t.name = 'Bring Equipment Bag' AND p.name = 'Ian Thomas') OR
    (t.name = 'Set Up Goals' AND p.name = 'Kevin White') OR
    (t.name = 'Match Report' AND p.name = 'Alex Johnson')
)
ON CONFLICT (task_id, player_id, fixture_id) DO NOTHING;

-- =========================
-- 8. SAMPLE RATINGS (from a previous match)
-- =========================
INSERT INTO ratings (team_id, player_id, fixture_id, rating, comment)
SELECT 
    '0854829d-445c-4138-9fd3-4db562ea46ee',
    p.id,
    f.id,
    CASE 
        WHEN p.name = 'Alex Johnson' THEN 8
        WHEN p.name = 'Ben Smith' THEN 9
        WHEN p.name = 'Charlie Brown' THEN 7
        WHEN p.name = 'David Wilson' THEN 8
        WHEN p.name = 'Ethan Davis' THEN 6
        WHEN p.name = 'Frank Miller' THEN 7
        WHEN p.name = 'George Taylor' THEN 8
        WHEN p.name = 'Harry Anderson' THEN 5
        WHEN p.name = 'Ian Thomas' THEN 7
        WHEN p.name = 'Jack Jackson' THEN 6
        WHEN p.name = 'Kevin White' THEN 7
        WHEN p.name = 'Liam Harris' THEN 8
        WHEN p.name = 'Mike Clark' THEN 6
        WHEN p.name = 'Nick Lewis' THEN 7
        WHEN p.name = 'Oscar Walker' THEN 8
    END,
    CASE 
        WHEN p.name = 'Alex Johnson' THEN 'Great leadership and solid defending'
        WHEN p.name = 'Ben Smith' THEN 'Excellent captain performance, scored the winner'
        WHEN p.name = 'Charlie Brown' THEN 'Good midfield control and passing'
        WHEN p.name = 'David Wilson' THEN 'Strong defensive display'
        WHEN p.name = 'Ethan Davis' THEN 'Decent performance, could improve finishing'
        WHEN p.name = 'Frank Miller' THEN 'Good impact as substitute'
        WHEN p.name = 'George Taylor' THEN 'Excellent work rate and energy'
        WHEN p.name = 'Harry Anderson' THEN 'Struggled with pace, needs improvement'
        WHEN p.name = 'Ian Thomas' THEN 'Solid performance when called upon'
        WHEN p.name = 'Jack Jackson' THEN 'Limited time but showed promise'
        WHEN p.name = 'Kevin White' THEN 'Good technical ability'
        WHEN p.name = 'Liam Harris' THEN 'Excellent team player'
        WHEN p.name = 'Mike Clark' THEN 'Decent performance, room for improvement'
        WHEN p.name = 'Nick Lewis' THEN 'Good tactical understanding'
        WHEN p.name = 'Oscar Walker' THEN 'Strong physical presence and good positioning'
    END
FROM players p
CROSS JOIN fixtures f
WHERE p.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.opponent = 'Red Lions FC'
ON CONFLICT (player_id, fixture_id) DO NOTHING;

-- =========================
-- 9. SAMPLE SQUAD SELECTIONS (for first fixture) - FIXED to use team_members.id
-- =========================
INSERT INTO squad_selections (fixture_id, player_id, status)
SELECT 
    f.id,
    tm.id,
    CASE 
        WHEN p.name IN ('Alex Johnson', 'Ben Smith', 'Charlie Brown', 'David Wilson', 'Ethan Davis') THEN 'selected'
        WHEN p.name IN ('Frank Miller', 'George Taylor', 'Harry Anderson', 'Ian Thomas', 'Kevin White') THEN 'substitute'
        ELSE 'reserve'
    END
FROM players p
JOIN team_members tm ON p.id = tm.player_id
CROSS JOIN fixtures f
WHERE p.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
AND f.opponent = 'Red Lions FC'
AND p.name IN ('Alex Johnson', 'Ben Smith', 'Charlie Brown', 'David Wilson', 'Ethan Davis', 'Frank Miller', 'George Taylor', 'Harry Anderson', 'Ian Thomas', 'Kevin White')
ON CONFLICT (fixture_id, player_id) DO NOTHING;

-- =========================
-- 10. SAMPLE COMMAND LOGS (for testing dual-channel architecture)
-- =========================
INSERT INTO command_logs (team_id, chat_id, user_id, username, command, arguments, success, executed_at) VALUES
-- Main team chat commands
('0854829d-445c-4138-9fd3-4db562ea46ee', '-4959662544', '123456789', 'alex_admin', 'get_all_players', '{}', TRUE, NOW() - INTERVAL '1 hour'),
('0854829d-445c-4138-9fd3-4db562ea46ee', '-4959662544', '123456789', 'alex_admin', 'get_fixtures', '{"upcoming_only": true}', TRUE, NOW() - INTERVAL '30 minutes'),
('0854829d-445c-4138-9fd3-4db562ea46ee', '-4959662544', '987654321', 'frank_player', 'get_availability', '{"fixture_id": "sample-fixture-id"}', TRUE, NOW() - INTERVAL '15 minutes'),
('0854829d-445c-4138-9fd3-4db562ea46ee', '-4959662544', '555666777', 'george_player', 'set_availability', '{"player_id": "sample-player-id", "fixture_id": "sample-fixture-id", "status": "Available"}', TRUE, NOW() - INTERVAL '10 minutes'),

-- Leadership chat commands (will be populated when leadership chat is created)
('0854829d-445c-4138-9fd3-4db562ea46ee', 'LEADERSHIP_CHAT_ID', '123456789', 'alex_admin', 'get_team_info', '{}', TRUE, NOW() - INTERVAL '2 hours'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'LEADERSHIP_CHAT_ID', '123456789', 'alex_admin', 'get_team_members', '{"active_only": true}', TRUE, NOW() - INTERVAL '1 hour 30 minutes'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'LEADERSHIP_CHAT_ID', '111222333', 'ben_manager', 'get_members_by_role', '{"role": "admin"}', TRUE, NOW() - INTERVAL '45 minutes'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'LEADERSHIP_CHAT_ID', '444555666', 'charlie_secretary', 'add_team_member', '{"name": "New Player", "role": "player", "phone": "+447123456999"}', TRUE, NOW() - INTERVAL '20 minutes'),

-- Failed commands for testing error handling
('0854829d-445c-4138-9fd3-4db562ea46ee', '-4959662544', '999888777', 'unknown_user', 'invalid_command', '{}', FALSE, NOW() - INTERVAL '5 minutes'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'LEADERSHIP_CHAT_ID', '777666555', 'unauthorized_user', 'get_team_info', '{}', FALSE, NOW() - INTERVAL '3 minutes'); 