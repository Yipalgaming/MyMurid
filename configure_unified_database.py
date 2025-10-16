#!/usr/bin/env python3
"""
Script to configure local development to use the online database
"""

import os
import requests

def get_online_database_url():
    """Get the online database URL from Render"""
    # You'll need to get this from your Render dashboard
    # Go to your Render service -> Environment tab -> DATABASE_URL
    print("To get your online database URL:")
    print("1. Go to https://dashboard.render.com")
    print("2. Select your PostgreSQL service")
    print("3. Go to the 'Environment' tab")
    print("4. Copy the DATABASE_URL value")
    print()
    
    database_url = input("Enter your Render DATABASE_URL: ").strip()
    
    if not database_url:
        print("❌ No database URL provided")
        return None
    
    if not database_url.startswith('postgresql://'):
        print("❌ Invalid database URL format")
        return None
    
    return database_url

def test_database_connection(database_url):
    """Test if we can connect to the online database"""
    try:
        from sqlalchemy import create_engine, text
        
        print("Testing connection to online database...")
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.fetchone():
                print("✅ Successfully connected to online database!")
                return True
    except Exception as e:
        print(f"❌ Failed to connect to online database: {e}")
        return False
    
    return False

def create_env_file(database_url):
    """Create a .env file for local development"""
    env_content = f"""# Local development environment variables
# This file uses the online database for consistency

# Database configuration
DATABASE_URL={database_url}

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Security (use different secret key for local development)
SECRET_KEY=local-dev-secret-key-{os.urandom(16).hex()}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file for local development")

def update_gitignore():
    """Update .gitignore to exclude .env file"""
    gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Updated .gitignore to exclude .env file")

def main():
    print("🔗 Configuring Local Development to Use Online Database")
    print("=" * 60)
    
    # Get database URL
    database_url = get_online_database_url()
    if not database_url:
        return
    
    # Test connection
    if not test_database_connection(database_url):
        print("\n❌ Cannot proceed without a working database connection")
        return
    
    # Create .env file
    create_env_file(database_url)
    
    # Update .gitignore
    update_gitignore()
    
    print("\n🎉 Configuration Complete!")
    print("\nNext steps:")
    print("1. Install python-dotenv: pip install python-dotenv")
    print("2. Update your app.py to load .env file:")
    print("   from dotenv import load_dotenv")
    print("   load_dotenv()")
    print("3. Restart your Flask app")
    print("4. Your local development will now use the online database!")
    
    print(f"\n📊 Database URL: {database_url[:50]}...")

if __name__ == "__main__":
    main()
