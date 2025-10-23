# 🐘 PostgreSQL Setup Guide for MyMurid

This guide will help you set up PostgreSQL for your MyMurid kiosk system.

## 📋 Prerequisites

- Windows 10/11
- Python 3.8+ with pip
- Administrator access to your computer

## 🚀 Step 1: Install PostgreSQL

### Option A: Official Installer (Recommended)

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Choose version 15 or 16 (latest stable)

2. **Run the Installer:**
   - **Installation Directory:** Keep default (`C:\Program Files\PostgreSQL\15\`)
   - **Data Directory:** Keep default (`C:\Program Files\PostgreSQL\15\data\`)
   - **Password:** Set a **strong password** (remember this!)
   - **Port:** Keep default `5432`
   - **Locale:** Keep default

3. **Installation Options:**
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4 (GUI tool)
   - ✅ Command Line Tools
   - ✅ Stack Builder (optional)

### Option B: Using Chocolatey (if available)

```powershell
choco install postgresql
```

## 🔧 Step 2: Install Python Dependencies

After PostgreSQL is installed, install the Python driver:

```bash
pip install psycopg2-binary==2.9.9
```

If that fails, try the alternative:

```bash
pip install asyncpg==0.29.0
```

## 🗄️ Step 3: Set Up Database

Run the setup script:

```bash
python setup_postgresql.py
```

This will:
- Create a database called `mymurid_db`
- Create a user called `mymurid_user`
- Set up proper permissions
- Create a `.env` file with database configuration

## 🔐 Step 4: Configure Environment

The setup script creates a `.env` file. You can also create it manually:

```env
# MyMurid Database Configuration
FLASK_ENV=production
DATABASE_URL=postgresql://mymurid_user:mymurid_password_2025@localhost:5432/mymurid_db
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## 🚀 Step 5: Initialize Database

Create the database tables:

```bash
python setup_db.py
```

## 🎯 Step 6: Start Your App

```bash
python app.py
```

## 🔍 Troubleshooting

### Common Issues:

1. **"pg_config executable not found"**
   - PostgreSQL is not installed or not in PATH
   - Reinstall PostgreSQL and ensure "Command Line Tools" is selected

2. **"Connection refused"**
   - PostgreSQL service is not running
   - Start PostgreSQL service in Windows Services

3. **"Authentication failed"**
   - Wrong password for postgres user
   - Reset password using pgAdmin or command line

### Check PostgreSQL Status:

```powershell
# Check if PostgreSQL service is running
Get-Service postgresql*

# Start PostgreSQL service if stopped
Start-Service postgresql*
```

### Reset PostgreSQL Password:

1. Open pgAdmin 4
2. Right-click on "PostgreSQL 15" → "Properties"
3. Go to "Connection" tab
4. Change password

## 📊 Database Management

### Using pgAdmin 4:
- **Host:** localhost
- **Port:** 5432
- **Database:** postgres (for admin)
- **Username:** postgres
- **Password:** (the one you set during installation)

### Using Command Line:
```bash
# Connect to database
psql -h localhost -U mymurid_user -d mymurid_db

# List tables
\dt

# Exit
\q
```

## 🔒 Security Notes

- Change default passwords
- Use strong passwords
- Limit database access to necessary users only
- Consider using SSL connections in production

## 📈 Performance Tips

- PostgreSQL will automatically handle multiple concurrent connections
- The system can handle hundreds of students ordering simultaneously
- Consider adding indexes for frequently queried fields

## 🎉 Success!

Once everything is working:
- Your MyMurid system will use PostgreSQL instead of SQLite
- Better performance and reliability
- Multi-user support
- Professional-grade database

## 📞 Need Help?

If you encounter issues:
1. Check the error messages carefully
2. Verify PostgreSQL is running
3. Check your passwords
4. Ensure all Python dependencies are installed

---

**Happy coding with your new PostgreSQL-powered MyMurid system! 🎯**
