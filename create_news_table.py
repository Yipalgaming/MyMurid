"""
Script to create the news table in the database
Run this to add the news table if it doesn't exist
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return None
    return db_url

def create_news_table():
    """Create the news table"""
    db_url = get_database_url()
    if not db_url:
        return False
    
    print("=" * 60)
    print("📰 Creating News Table")
    print("=" * 60)
    print()
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'news'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("ℹ️  News table already exists. Skipping creation.")
            cursor.close()
            conn.close()
            return True
        
        print("📝 Creating news table...")
        
        # Create the table
        cursor.execute("""
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
        """)
        
        # Create indexes
        print("📝 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_is_published ON news(is_published);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_priority ON news(priority);")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ News table created successfully!")
        print("=" * 60)
        print()
        print("The news table is now ready to use.")
        print("You can create news items through the admin panel.")
        return True
        
    except psycopg2.Error as e:
        print()
        print("❌ Error creating news table:")
        print(f"   {e}")
        return False
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    create_news_table()

