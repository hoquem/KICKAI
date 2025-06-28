-- Check Fixtures Table Structure
-- Run this in your Supabase SQL Editor to diagnose the issue

-- Check if fixtures table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'fixtures'
) as table_exists;

-- If table exists, show its structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'fixtures' 
ORDER BY ordinal_position;

-- Show any existing data
SELECT * FROM fixtures LIMIT 5;

-- Show table constraints
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'fixtures'::regclass;
