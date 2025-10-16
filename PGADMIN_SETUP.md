# Render PostgreSQL Database Connection Details for pgAdmin4

## Connection Information:
- **Host/Server:** dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com
- **Port:** 5432 (default PostgreSQL port)
- **Database:** mymurid_db
- **Username:** mymurid_user
- **Password:** 0bPbfFQET4Eck6afDWzkO7VXFeHylLc3

## pgAdmin4 Setup Steps:

### 1. Open pgAdmin4
- Launch pgAdmin4 application
- If not installed, download from: https://www.pgadmin.org/download/

### 2. Create New Server Connection
- Right-click on "Servers" in the left panel
- Select "Create" → "Server..."

### 3. General Tab
- **Name:** MyMurid Render Database (or any name you prefer)

### 4. Connection Tab
- **Host name/address:** dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com
- **Port:** 5432
- **Maintenance database:** mymurid_db
- **Username:** mymurid_user
- **Password:** 0bPbfFQET4Eck6afDWzkO7VXFeHylLc3

### 5. Advanced Tab (Optional)
- **DB restriction:** mymurid_db (to only show this database)

### 6. Save Connection
- Click "Save" to create the connection

## What You'll See:
Once connected, you can explore:
- **Tables:** student_info, menu_item, order, vote, feedback, etc.
- **Data:** All your students, orders, votes, and other data
- **Schema:** Database structure and relationships

## Security Note:
- This connection uses SSL by default (Render requirement)
- Your password is stored securely in pgAdmin4
- Connection is encrypted

## Troubleshooting:
- If connection fails, check if your IP is whitelisted on Render
- Render allows connections from any IP by default
- Make sure you're using the correct port (5432)
