-- SQL script to update ic_number column to support Unicode characters (Chinese, symbols, etc.)
-- Run this in pgAdmin or your PostgreSQL client

-- For PostgreSQL, we need to alter the column to allow longer strings
-- The column is currently VARCHAR(4), we need to change it to VARCHAR(50)

ALTER TABLE student_info 
ALTER COLUMN ic_number TYPE VARCHAR(50);

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'student_info' AND column_name = 'ic_number';

-- Note: This change allows IC numbers to contain:
-- - Unicode characters (Chinese, Japanese, Korean, etc.)
-- - Symbols (!@#$%^&*, etc.)
-- - Emojis
-- - Any combination of the above (up to 50 characters)

