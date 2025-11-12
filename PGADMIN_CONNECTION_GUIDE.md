# 📘 How to Connect to PostgreSQL Database using pgAdmin 4

This guide will help you connect to your PostgreSQL database using pgAdmin 4.

## 🚨 Quick Fix for "Server closed the connection unexpectedly"

If you're getting this error, try these steps **in order**:

1. **Check Hostname (CRITICAL):**
   - Go to your Render dashboard → PostgreSQL database
   - Copy the **exact** hostname from the connection string
   - Your error shows `dpg-d2pt6mbd5dus73bejrog-a` but it might be `dpg-d2pt6mbe5dus73bejrog-a`
   - Update the hostname in pgAdmin to match exactly

2. **Wake Up the Database:**
   - Render free tier databases sleep after inactivity
   - Go to Render dashboard → Your database → Click "Wake" or "Resume"
   - Wait 30-60 seconds, then try connecting again

3. **Increase Connection Timeout:**
   - In pgAdmin Connection tab, set "Connection timeout" to 30 or 60 seconds

4. **Verify Database Status:**
   - Check Render dashboard that database status is "Available" (not "Paused" or "Sleeping")

## 🔍 Step 1: Your Render Database Connection Details

Since you're using a **Render database**, here are your connection details:

### Render Database Connection:
- **Host/Server:** `dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com`
- **Port:** `5432`
- **Database:** `mymurid_db`
- **Username:** `mymurid_user`
- **Password:** `0bPbfFQET4Eck6afDWzkO7VXFeHylLc3`

> ⚠️ **Important:** Render databases require SSL connections!

## 🚀 Step 2: Open pgAdmin 4

1. **Launch pgAdmin 4** from your Start Menu or Applications folder
2. If you haven't installed it yet, download from: https://www.pgadmin.org/download/
3. You may need to set a master password when you first open it (remember this!)

## 🔌 Step 3: Create a New Server Connection

1. **In the left panel**, right-click on **"Servers"**
2. Select **"Create"** → **"Server..."**

## 📝 Step 4: Fill in Connection Details

### General Tab:
- **Name:** Enter a friendly name (e.g., "MyMurid Render Database" or "Canteen Kiosk - Render")

### Connection Tab:
Fill in the following fields with your **Render database** details:

- **Host name/address:** `dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com`
  
- **Port:** `5432`

- **Maintenance database:** `mymurid_db`

- **Username:** `mymurid_user`

- **Password:** `0bPbfFQET4Eck6afDWzkO7VXFeHylLc3`
  - ✅ Check "Save password" to avoid entering it every time

### Advanced Tab (Optional):
- **DB restriction:** `mymurid_db` (to only show this database)

### SSL Tab (⚠️ REQUIRED for Render):
**This is important!** Render databases require SSL connections, but sometimes need special settings:

**Option 1: Try Prefer Mode (Recommended First)**
1. Click on the **"SSL"** tab
2. Set **SSL mode:** `Prefer`
3. Leave all other SSL fields empty/default
4. Click Save and try connecting

**Option 2: If Prefer doesn't work, try Allow Mode**
1. Set **SSL mode:** `Allow`
2. Leave all other SSL fields empty/default
3. Click Save and try connecting

**Option 3: Disable Certificate Verification (If above don't work)**
1. Set **SSL mode:** `Prefer` or `Require`
2. Check the box for **"SSL Compression"** (if available)
3. In **"Root certificate"** field, leave empty OR browse to find a certificate file (usually not needed)
4. **Important:** You may need to disable certificate verification in pgAdmin settings:
   - Go to File → Preferences → Browser → Display
   - Or try setting SSL mode to `Allow` which is more permissive

> ⚠️ **If you get "SSL connection has been closed unexpectedly":**
> - Try SSL mode: `Allow` (most permissive)
> - Or try SSL mode: `Prefer` 
> - Make sure all certificate fields are empty
> - Some users report success with SSL mode: `Disable` (not recommended but works for some)

## 💾 Step 5: Save and Connect

1. Click **"Save"** button
2. pgAdmin will attempt to connect
3. If successful, you'll see your server appear in the left panel
4. Expand it to see your databases

## 🔍 Step 6: Navigate Your Database

Once connected:

1. **Expand your server** in the left panel
2. **Expand "Databases"**
3. **Expand your database** (e.g., `mymurid_db`)
4. **Expand "Schemas"** → **"public"** → **"Tables"**
5. You'll see all your tables:
   - `student_info`
   - `menu_item`
   - `order`
   - `feedback`
   - `vote`
   - `top_up`
   - `payment`
   - `directory`
   - And more...

## 🛠️ Common Operations in pgAdmin 4

### View Table Data:
- Right-click on a table → **"View/Edit Data"** → **"All Rows"**

### Run SQL Queries:
- Right-click on your database → **"Query Tool"**
- Type your SQL query
- Click the **"Execute"** button (▶️) or press `F5`

### Edit Data:
- Right-click on a table → **"View/Edit Data"** → **"All Rows"**
- Click on any cell to edit
- Click **"Save"** to commit changes

## ❌ Troubleshooting

### Connection Refused / Cannot Connect / "Server closed the connection unexpectedly":
- **For Render database:**
  
  **⚠️ IMPORTANT: Check Hostname!**
  - Your error shows: `dpg-d2pt6mbd5dus73bejrog-a` (with "mbd")
  - But the correct one should be: `dpg-d2pt6mbe5dus73bejrog-a` (with "mbe")
  - **Double-check your Render dashboard** for the exact hostname!
  - Copy the hostname directly from Render dashboard → Your Database → Internal Database URL or Connection String
  
  **Common Causes:**
  1. **Database is Sleeping (Most Common on Free Tier):**
     - Render free tier databases sleep after 90 days of inactivity
     - **Solution:** Go to your Render dashboard → Wake up the database
     - Or make a connection from your app first to wake it up
     - Wait 30-60 seconds after waking up before connecting
  
  2. **Database is Paused:**
     - Check Render dashboard to see if database status is "Paused"
     - Click "Resume" if paused
  
  3. **Wrong Hostname:**
     - Verify the exact hostname in Render dashboard
     - It should match exactly (case-sensitive)
  
  4. **Connection Timeout:**
     - Increase "Connection timeout" to 30 or 60 seconds in pgAdmin
     - Go to Connection tab → Connection timeout (seconds)
  
  5. **Network/Firewall:**
     - Check your internet connection
     - Try from a different network
     - Some corporate networks block database connections

### Authentication Failed:
- **Verify username and password:**
  - Username: `mymurid_user`
  - Password: `0bPbfFQET4Eck6afDWzkO7VXFeHylLc3`
  - Make sure there are no extra spaces when copying/pasting
  - Check your Render dashboard if credentials have changed

### SSL Connection Error / "SSL connection has been closed unexpectedly":
- **This is the most common issue with Render databases:**
  
  **Solution 1: Change SSL Mode (Try in this order):**
  1. Open your server connection settings
  2. Go to **SSL tab**
  3. Try these SSL modes in order:
     - First: `Prefer`
     - Second: `Allow` 
     - Third: `Disable` (not secure but sometimes works)
  4. **Leave ALL certificate fields empty** (Root certificate, Client certificate, etc.)
  5. Save and try connecting again

  **Solution 2: Check pgAdmin Version:**
  - Older versions of pgAdmin sometimes have SSL issues
  - Update to the latest version: https://www.pgadmin.org/download/
  
  **Solution 3: Alternative Connection Method:**
  - If pgAdmin continues to fail, try using **DBeaver** (free alternative):
    - Download: https://dbeaver.io/download/
    - It often handles Render SSL connections better
    - Use the same connection details
  
  **Solution 4: Use psql Command Line (Advanced):**
  - If GUI tools fail, you can use command line:
  ```bash
  psql "postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db?sslmode=require"
  ```

### "Database does not exist":
- **For Render:**
  - The database `mymurid_db` should already exist
  - If you see this error, check the **Maintenance database** field - it should be `mymurid_db`
  - You can also try `postgres` as the maintenance database first, then navigate to `mymurid_db`

## 📋 Quick Reference: Your Render Connection String

Your Render database connection string is:
```
postgresql://mymurid_user:0bPbfFQET4Eck6afDWzkO7VXFeHylLc3@dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com:5432/mymurid_db
```

Breakdown:
- **Username:** `mymurid_user`
- **Password:** `0bPbfFQET4Eck6afDWzkO7VXFeHylLc3`
- **Host:** `dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com`
- **Port:** `5432`
- **Database:** `mymurid_db`
- **SSL:** Required (set in pgAdmin SSL tab)

## 🔐 Security Tips

1. **Don't share your database password**
2. **Use strong passwords** in production
3. **Enable SSL** for remote connections
4. **Limit database access** to authorized users only
5. **Regular backups** are important!

## 📞 Need Help?

If you're still having trouble:
1. Check your `.env` file for the exact connection details
2. Verify PostgreSQL is installed and running
3. Check the PostgreSQL logs for error messages
4. Make sure you're using the correct port (default is 5432)

