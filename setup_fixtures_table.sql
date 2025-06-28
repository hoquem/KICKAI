-- Create fixtures table for KICKAI
-- This table stores all team fixtures/matches

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_fixtures_team_id ON fixtures(team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_match_date ON fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(status);
CREATE INDEX IF NOT EXISTS idx_fixtures_team_date ON fixtures(team_id, match_date);

-- Enable Row Level Security (RLS)
ALTER TABLE fixtures ENABLE ROW LEVEL SECURITY;

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON fixtures TO authenticated;
