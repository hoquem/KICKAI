-- KICKAI Database Setup
-- Complete database schema for KICKAI football team management system
-- Run this in your Supabase SQL Editor

-- ========================================
-- TEAMS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS teams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- TEAM MEMBERS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS team_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'player' CHECK (role IN ('admin', 'captain', 'secretary', 'manager', 'player')),
    phone_number VARCHAR(20),
    telegram_user_id VARCHAR(50),
    telegram_username VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- TEAM BOTS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS team_bots (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    bot_token VARCHAR(100) NOT NULL,
    bot_username VARCHAR(50),
    chat_id VARCHAR(50),
    leadership_chat_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- FIXTURES TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS fixtures (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    opponent VARCHAR(100) NOT NULL,
    match_date DATE NOT NULL,
    kickoff_time TIME NOT NULL,
    venue VARCHAR(200) NOT NULL,
    competition VARCHAR(50) DEFAULT 'League',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'postponed')),
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- COMMAND LOGS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS command_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    chat_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    username VARCHAR(50),
    command VARCHAR(50) NOT NULL,
    arguments TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================
CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_telegram_id ON team_members(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_role ON team_members(role);
CREATE INDEX IF NOT EXISTS idx_team_bots_team_id ON team_bots(team_id);
CREATE INDEX IF NOT EXISTS idx_team_bots_chat_id ON team_bots(chat_id);
CREATE INDEX IF NOT EXISTS idx_team_bots_leadership_chat_id ON team_bots(leadership_chat_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_team_id ON fixtures(team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_match_date ON fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(status);
CREATE INDEX IF NOT EXISTS idx_command_logs_team_id ON command_logs(team_id);
CREATE INDEX IF NOT EXISTS idx_command_logs_chat_id ON command_logs(chat_id);
CREATE INDEX IF NOT EXISTS idx_command_logs_created_at ON command_logs(created_at);

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE fixtures ENABLE ROW LEVEL SECURITY;
ALTER TABLE command_logs ENABLE ROW LEVEL SECURITY;

-- ========================================
-- PERMISSIONS
-- ========================================
GRANT SELECT, INSERT, UPDATE, DELETE ON teams TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON team_members TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON team_bots TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON fixtures TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON command_logs TO authenticated;

-- ========================================
-- SAMPLE DATA
-- ========================================

-- Insert sample team
INSERT INTO teams (id, name) VALUES 
('0854829d-445c-4138-9fd3-4db562ea46ee', 'BP Hatters FC')
ON CONFLICT (name) DO NOTHING;

-- Insert sample team members
INSERT INTO team_members (team_id, name, role, phone_number, telegram_user_id, telegram_username) VALUES
('0854829d-445c-4138-9fd3-4db562ea46ee', 'Mahmud', 'admin', '+1234567890', '1581500055', 'doods2000'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'John Smith', 'captain', '+1234567891', '1234567890', 'johnsmith'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'Mike Johnson', 'secretary', '+1234567892', '1234567891', 'mikejohnson')
ON CONFLICT DO NOTHING;

-- Insert sample team bot
INSERT INTO team_bots (team_id, bot_token, bot_username, chat_id, leadership_chat_id) VALUES
('0854829d-445c-4138-9fd3-4db562ea46ee', '7569851581:AAFh2uvMIqbd_aGXKV2BBZ_fY-89NWG3ct0', 'BPHatters_bot', '-4959662544', '-4611381628')
ON CONFLICT DO NOTHING;

-- Insert sample fixtures
INSERT INTO fixtures (team_id, opponent, match_date, kickoff_time, venue, competition, notes, created_by) VALUES
('0854829d-445c-4138-9fd3-4db562ea46ee', 'Thunder FC', '2024-07-15', '14:00:00', 'Home - Central Park', 'League', 'Red kit required, arrive 30 minutes early', '1581500055'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'Lightning United', '2024-07-22', '15:30:00', 'Away - Lightning Ground', 'League', 'Blue kit, car sharing available', '1581500055'),
('0854829d-445c-4138-9fd3-4db562ea46ee', 'Storm Rovers', '2024-08-05', '16:00:00', 'Home - Central Park', 'Cup', 'Quarter final - all hands on deck!', '1581500055')
ON CONFLICT DO NOTHING;

-- ========================================
-- VERIFICATION QUERIES
-- ========================================
SELECT 'Database setup completed successfully!' as status;

SELECT 'Teams:' as table_name, COUNT(*) as count FROM teams
UNION ALL
SELECT 'Team Members:', COUNT(*) FROM team_members
UNION ALL
SELECT 'Team Bots:', COUNT(*) FROM team_bots
UNION ALL
SELECT 'Fixtures:', COUNT(*) FROM fixtures
UNION ALL
SELECT 'Command Logs:', COUNT(*) FROM command_logs;
