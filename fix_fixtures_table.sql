-- Fix Fixtures Table Structure
-- Run this in your Supabase SQL Editor

-- First, let's see what columns currently exist
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'fixtures' 
ORDER BY ordinal_position;

-- Drop the existing table if it has wrong structure
DROP TABLE IF EXISTS fixtures CASCADE;

-- Create fixtures table with correct structure
CREATE TABLE fixtures (
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

-- Create indexes
CREATE INDEX idx_fixtures_team_id ON fixtures(team_id);
CREATE INDEX idx_fixtures_match_date ON fixtures(match_date);
CREATE INDEX idx_fixtures_status ON fixtures(status);

-- Enable RLS
ALTER TABLE fixtures ENABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON fixtures TO authenticated;

-- Insert sample fixtures
INSERT INTO fixtures (team_id, opponent, match_date, kickoff_time, venue, competition, notes, created_by) VALUES
(
    '0854829d-445c-4138-9fd3-4db562ea46ee',  -- Replace with your actual team_id
    'Thunder FC',
    '2024-07-15',
    '14:00:00',
    'Home - Central Park',
    'League',
    'Red kit required, arrive 30 minutes early',
    '1581500055'
),
(
    '0854829d-445c-4138-9fd3-4db562ea46ee',  -- Replace with your actual team_id
    'Lightning United',
    '2024-07-22',
    '15:30:00',
    'Away - Lightning Ground',
    'League',
    'Blue kit, car sharing available',
    '1581500055'
),
(
    '0854829d-445c-4138-9fd3-4db562ea46ee',  -- Replace with your actual team_id
    'Storm Rovers',
    '2024-08-05',
    '16:00:00',
    'Home - Central Park',
    'Cup',
    'Quarter final - all hands on deck!',
    '1581500055'
);

-- Verify the table was created correctly
SELECT COUNT(*) as fixture_count FROM fixtures;

-- Show the table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'fixtures' 
ORDER BY ordinal_position; 