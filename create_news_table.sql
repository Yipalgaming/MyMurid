-- Migration script to create the news table
-- This script is idempotent and safe to run multiple times

-- Step 1: Create the news table (if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'news'
    ) THEN
        CREATE TABLE news (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            is_published BOOLEAN DEFAULT TRUE,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT fk_news_author FOREIGN KEY (author_id) REFERENCES student_info(id)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_news_is_published ON news(is_published);
        CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);
        CREATE INDEX IF NOT EXISTS idx_news_priority ON news(priority);
        
        RAISE NOTICE 'News table created successfully';
    ELSE
        RAISE NOTICE 'News table already exists';
    END IF;
END $$;

-- Verify the table was created
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'news' 
ORDER BY ordinal_position;

