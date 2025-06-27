-- Multi-Team Support Schema for KICKAI
-- This adds team management capabilities to the existing system

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    whatsapp_group VARCHAR(255) NOT NULL,
    created_by VARCHAR(20) NOT NULL, -- phone number of admin
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Team members table (links users to teams with roles)
CREATE TABLE IF NOT EXISTS team_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE SET NULL, -- optional link to player record
    phone_number VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'player', -- admin, manager, captain, secretary, player
    is_active BOOLEAN DEFAULT true,
    invited_by VARCHAR(20), -- phone number of who invited them
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id, phone_number)
);

-- Add team_id to existing tables to support multi-team
ALTER TABLE players ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE SET NULL;
ALTER TABLE fixtures ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE CASCADE;
ALTER TABLE availability ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE CASCADE;
ALTER TABLE ratings ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE CASCADE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE CASCADE;
ALTER TABLE task_assignments ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE CASCADE;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE CASCADE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_teams_active ON teams(is_active);
CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_phone ON team_members(phone_number);
CREATE INDEX IF NOT EXISTS idx_team_members_role ON team_members(role);

-- Add comments for documentation
COMMENT ON TABLE teams IS 'Stores team information for multi-team support';
COMMENT ON TABLE team_members IS 'Links users to teams with specific roles';
COMMENT ON COLUMN team_members.role IS 'Role in the team: admin, manager, captain, secretary, player';
COMMENT ON COLUMN team_members.player_id IS 'Optional link to player record for full integration';

-- Insert default team for existing data (if needed)
-- This creates a default team for any existing data
INSERT INTO teams (name, description, whatsapp_group, created_by, is_active)
VALUES (
    'KICKAI Default Team',
    'Default team for existing data',
    'default_whatsapp_group',
    'system',
    true
) ON CONFLICT DO NOTHING;

-- Update existing data to link to default team (if needed)
-- This is optional and can be run manually if needed
-- UPDATE players SET team_id = (SELECT id FROM teams WHERE name = 'KICKAI Default Team') WHERE team_id IS NULL;
-- UPDATE fixtures SET team_id = (SELECT id FROM teams WHERE name = 'KICKAI Default Team') WHERE team_id IS NULL;
-- etc. 