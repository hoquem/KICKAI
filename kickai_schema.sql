-- KICKAI Full Database Schema (Clean Install)
-- Drops all existing tables and recreates the schema from scratch
-- Includes a sample team and bot mapping for BP Hatters FC
-- Updated for dual-channel architecture (main team + leadership groups)

-- =========================
-- 1. DROP EXISTING TABLES
-- =========================
DROP TABLE IF EXISTS command_logs CASCADE;
DROP TABLE IF EXISTS team_bots CASCADE;
DROP TABLE IF EXISTS squad_selections CASCADE;
DROP TABLE IF EXISTS availability CASCADE;
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS task_assignments CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS fixtures CASCADE;
DROP TABLE IF EXISTS team_members CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

-- =========================
-- 2. CREATE TABLES
-- =========================

-- Teams table
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    telegram_group VARCHAR(255),
    leadership_chat_id VARCHAR(255),
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
COMMENT ON TABLE teams IS 'Stores team information for multi-team support';

-- Players table
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL
);
COMMENT ON TABLE players IS 'Stores player information';

-- Team members table
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE SET NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    position VARCHAR(100),
    role VARCHAR(50) DEFAULT 'player',
    telegram_username VARCHAR(100),
    telegram_user_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id, phone),
    UNIQUE(team_id, email)
);
COMMENT ON TABLE team_members IS 'Links users to teams with specific roles';

-- Fixtures table
CREATE TABLE fixtures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    opponent VARCHAR(255) NOT NULL,
    match_date TIMESTAMP WITH TIME ZONE NOT NULL,
    venue VARCHAR(255),
    home_away VARCHAR(10) DEFAULT 'home',
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE fixtures IS 'Stores match fixtures for teams';

-- Squad selections table
CREATE TABLE squad_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id UUID NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES team_members(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'selected',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(fixture_id, player_id)
);
COMMENT ON TABLE squad_selections IS 'Tracks which players are selected for which fixture';

-- Availability table
CREATE TABLE availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    fixture_id UUID NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'Available',
    squad_status VARCHAR(20),
    has_paid_fees BOOLEAN DEFAULT FALSE,
    fine_amount NUMERIC(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(player_id, fixture_id)
);
COMMENT ON TABLE availability IS 'Tracks player availability, payments, and fines for fixtures';

-- Ratings table
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    fixture_id UUID NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 10),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(player_id, fixture_id)
);
COMMENT ON TABLE ratings IS 'Peer-to-peer player ratings for each fixture';

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE tasks IS 'Recurring chores/tasks for teams';

-- Task assignments table
CREATE TABLE task_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    fixture_id UUID NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(task_id, player_id, fixture_id)
);
COMMENT ON TABLE task_assignments IS 'Tracks which player is assigned to which task for each fixture';

-- Equipment table
CREATE TABLE equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE equipment IS 'Tracks team equipment inventory';

-- Team bots table (Updated for dual-channel support)
CREATE TABLE team_bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    bot_token VARCHAR(255) NOT NULL,
    chat_id VARCHAR(255) NOT NULL,
    leadership_chat_id VARCHAR(255),
    bot_username VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id),
    UNIQUE(bot_token)
);
COMMENT ON TABLE team_bots IS 'Maps teams to their Telegram bot tokens and chat IDs (main + leadership)';

-- Command logs table (New for dual-channel architecture)
CREATE TABLE command_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    chat_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    command VARCHAR(100) NOT NULL,
    arguments TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE command_logs IS 'Audit trail for bot commands and natural language interactions';

-- =========================
-- 3. CREATE INDEXES
-- =========================
CREATE INDEX idx_teams_active ON teams(is_active);
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_phone ON team_members(phone);
CREATE INDEX idx_team_members_email ON team_members(email);
CREATE INDEX idx_team_members_role ON team_members(role);
CREATE INDEX idx_team_members_telegram_user_id ON team_members(telegram_user_id);
CREATE INDEX idx_fixtures_team_id ON fixtures(team_id);
CREATE INDEX idx_squad_selections_fixture_id ON squad_selections(fixture_id);
CREATE INDEX idx_squad_selections_player_id ON squad_selections(player_id);
CREATE INDEX idx_availability_team_id ON availability(team_id);
CREATE INDEX idx_availability_fixture_id ON availability(fixture_id);
CREATE INDEX idx_ratings_team_id ON ratings(team_id);
CREATE INDEX idx_ratings_fixture_id ON ratings(fixture_id);
CREATE INDEX idx_tasks_team_id ON tasks(team_id);
CREATE INDEX idx_task_assignments_team_id ON task_assignments(team_id);
CREATE INDEX idx_equipment_team_id ON equipment(team_id);
CREATE INDEX idx_team_bots_team_id ON team_bots(team_id);
CREATE INDEX idx_team_bots_active ON team_bots(is_active);
CREATE INDEX idx_team_bots_username ON team_bots(bot_username);
CREATE INDEX idx_command_logs_team_id ON command_logs(team_id);
CREATE INDEX idx_command_logs_chat_id ON command_logs(chat_id);
CREATE INDEX idx_command_logs_command ON command_logs(command);
CREATE INDEX idx_command_logs_executed_at ON command_logs(executed_at);

-- =========================
-- 4. SAMPLE DATA
-- =========================
-- Insert sample team
INSERT INTO teams (id, name, description, telegram_group, created_by, is_active)
VALUES (
    '0854829d-445c-4138-9fd3-4db562ea46ee',
    'BP Hatters',
    'Sunday League football team managed by AI',
    '@bphatters_group',
    'admin@kickai.com',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- Insert sample bot mapping (main team chat only - leadership chat will be added later)
INSERT INTO team_bots (team_id, bot_token, chat_id, bot_username, is_active)
VALUES (
    '0854829d-445c-4138-9fd3-4db562ea46ee',
    '7569851581:AAFh2uvMIqbd_aGXKV2BBZ_fY-89NWG3ct0',
    '-4959662544',
    '@bphatters_bot',
    TRUE
) ON CONFLICT (team_id) DO UPDATE SET
    bot_token = EXCLUDED.bot_token,
    chat_id = EXCLUDED.chat_id,
    bot_username = EXCLUDED.bot_username,
    updated_at = NOW();

-- Insert sample team members with roles for testing
INSERT INTO team_members (team_id, name, role, phone, telegram_username, is_active)
VALUES 
    ('0854829d-445c-4138-9fd3-4db562ea46ee', 'Admin User', 'admin', '+1234567890', 'admin_user', TRUE),
    ('0854829d-445c-4138-9fd3-4db562ea46ee', 'Secretary User', 'secretary', '+1234567891', 'secretary_user', TRUE),
    ('0854829d-445c-4138-9fd3-4db562ea46ee', 'Manager User', 'manager', '+1234567892', 'manager_user', TRUE),
    ('0854829d-445c-4138-9fd3-4db562ea46ee', 'Treasurer User', 'treasurer', '+1234567893', 'treasurer_user', TRUE),
    ('0854829d-445c-4138-9fd3-4db562ea46ee', 'Player One', 'player', '+1234567894', 'player_one', TRUE),
    ('0854829d-445c-4138-9fd3-4db562ea46ee', 'Player Two', 'player', '+1234567895', 'player_two', TRUE)
ON CONFLICT (team_id, phone) DO NOTHING; 