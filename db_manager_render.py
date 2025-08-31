#!/usr/bin/env python3
"""
Database Manager for Render
Web interface to manage your Render PostgreSQL database
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = 'render_db_manager_secret_key_2025'

# Render Database Connection Details
DB_CONFIG = {
    'host': 'dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com',
    'port': '5432',
    'database': 'mymurid_db',
    'user': 'mymurid_user',
    'password': '0bPbfFQET4Eck6afDWzkO7VXFeHylLc3',
    'sslmode': 'require'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def quote_table_name(table_name):
    """Quote table names to handle reserved keywords"""
    if table_name.lower() in ['order', 'user', 'group']:
        return f'"{table_name}"'
    return table_name

@app.route('/')
def index():
    """Show all tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template_string(INDEX_HTML, tables=tables)
    except Exception as e:
        return f"Error: {e}"

@app.route('/table/<table_name>')
def view_table(table_name):
    """View table contents"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        quoted_table = quote_table_name(table_name)
        cursor.execute(f"SELECT * FROM {quoted_table} LIMIT 100;")
        rows = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if rows else []
        
        cursor.close()
        conn.close()
        
        return render_template_string(TABLE_HTML, table_name=table_name, rows=rows, columns=columns)
    except Exception as e:
        return f"Error viewing table {table_name}: {e}"

@app.route('/edit/<table_name>/<int:row_id>', methods=['GET', 'POST'])
def edit_row(table_name, row_id):
    """Edit a row"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        quoted_table = quote_table_name(table_name)
        
        if request.method == 'POST':
            # Get form data and update
            cursor.execute(f"SELECT * FROM {quoted_table} LIMIT 1;")
            columns = [desc[0] for desc in cursor.description]
            
            # Build UPDATE query
            set_clauses = []
            values = []
            for col in columns:
                if col != 'id' and col in request.form:
                    set_clauses.append(f"{col} = %s")
                    values.append(request.form[col])
            
            if set_clauses:
                values.append(row_id)
                query = f"UPDATE {quoted_table} SET {', '.join(set_clauses)} WHERE id = %s"
                cursor.execute(query, values)
                conn.commit()
                flash(f"Row updated successfully in {table_name}!")
                return redirect(url_for('view_table', table_name=table_name))
        
        # GET: Show edit form
        cursor.execute(f"SELECT * FROM {quoted_table} WHERE id = %s;", (row_id,))
        row = cursor.fetchone()
        
        if not row:
            flash(f"Row {row_id} not found in {table_name}")
            return redirect(url_for('view_table', table_name=table_name))
        
        cursor.close()
        conn.close()
        
        return render_template_string(EDIT_HTML, table_name=table_name, row=row, row_id=row_id)
    except Exception as e:
        return f"Error editing row: {e}"

@app.route('/add/<table_name>', methods=['GET', 'POST'])
def add_row(table_name):
    """Add a new row"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        quoted_table = quote_table_name(table_name)
        
        if request.method == 'POST':
            # Get form data and insert
            cursor.execute(f"SELECT * FROM {quoted_table} LIMIT 1;")
            columns = [desc[0] for desc in cursor.description]
            
            # Build INSERT query
            insert_columns = []
            placeholders = []
            values = []
            for col in columns:
                if col != 'id' and col in request.form and request.form[col]:
                    insert_columns.append(col)
                    placeholders.append('%s')
                    values.append(request.form[col])
            
            if insert_columns:
                query = f"INSERT INTO {quoted_table} ({', '.join(insert_columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, values)
                conn.commit()
                flash(f"Row added successfully to {table_name}!")
                return redirect(url_for('view_table', table_name=table_name))
        
        # GET: Show add form
        cursor.execute(f"SELECT * FROM {quoted_table} LIMIT 1;")
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        cursor.close()
        conn.close()
        
        return render_template_string(ADD_HTML, table_name=table_name, columns=columns)
    except Exception as e:
        return f"Error adding row: {e}"

@app.route('/delete/<table_name>/<int:row_id>')
def delete_row(table_name, row_id):
    """Delete a row"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        quoted_table = quote_table_name(table_name)
        cursor.execute(f"DELETE FROM {quoted_table} WHERE id = %s;", (row_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash(f"Row {row_id} deleted from {table_name}!")
        return redirect(url_for('view_table', table_name=table_name))
    except Exception as e:
        return f"Error deleting row: {e}"

# HTML Templates
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Render Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .table-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .table-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
        .table-card h3 { margin: 0 0 15px 0; color: #007bff; }
        .table-card a { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        .table-card a:hover { background: #0056b3; }
        .status { text-align: center; padding: 20px; background: #d4edda; color: #155724; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Render Database Manager</h1>
        <p style="text-align: center; color: #666;">Manage your MyMurid database on Render</p>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="status">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="table-grid">
            {% for table in tables %}
            <div class="table-card">
                <h3>📋 {{ table[0] }}</h3>
                <a href="{{ url_for('view_table', table_name=table[0]) }}">View & Manage</a>
            </div>
            {% endfor %}
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>🔗 Connected to: dpg-d2pt6mbe5dus73bejrog-a.singapore-postgres.render.com</p>
        </div>
    </div>
</body>
</html>
"""

TABLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ table_name }} - Render Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .back-link { display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; }
        .add-btn { display: inline-block; margin-bottom: 20px; margin-left: 10px; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f5f5f5; }
        .action-btn { padding: 5px 10px; margin: 2px; text-decoration: none; border-radius: 3px; font-size: 12px; }
        .edit-btn { background: #ffc107; color: #212529; }
        .delete-btn { background: #dc3545; color: white; }
        .status { text-align: center; padding: 20px; background: #d4edda; color: #155724; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Table: {{ table_name }}</h1>
        
        <a href="{{ url_for('index') }}" class="back-link">← Back to Tables</a>
        <a href="{{ url_for('add_row', table_name=table_name) }}" class="add-btn">➕ Add New Row</a>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="status">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% if rows %}
        <table>
            <thead>
                <tr>
                    {% for column in columns %}
                    <th>{{ column }}</th>
                    {% endfor %}
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr>
                    {% for column in columns %}
                    <td>{{ row[column] }}</td>
                    {% endfor %}
                    <td>
                        <a href="{{ url_for('edit_row', table_name=table_name, row_id=row.id) }}" class="action-btn edit-btn">Edit</a>
                        <a href="{{ url_for('delete_row', table_name=table_name, row_id=row.id) }}" class="action-btn delete-btn" onclick="return confirm('Are you sure you want to delete this row?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No data found in this table.</p>
        {% endif %}
    </div>
</body>
</html>
"""

EDIT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Row - Render Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { padding: 10px 20px; margin-right: 10px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Edit Row in {{ table_name }}</h1>
        
        <form method="POST">
            {% for column in row.keys() %}
            {% if column != 'id' %}
            <div class="form-group">
                <label for="{{ column }}">{{ column }}:</label>
                {% if column in ['description', 'message', 'admin_response'] %}
                <textarea name="{{ column }}" rows="3">{{ row[column] or '' }}</textarea>
                {% else %}
                <input type="text" name="{{ column }}" value="{{ row[column] or '' }}">
                {% endif %}
            </div>
            {% endif %}
            {% endfor %}
            
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Update Row</button>
                <a href="{{ url_for('view_table', table_name=table_name) }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>
"""

ADD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Row - Render Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { padding: 10px 20px; margin-right: 10px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>➕ Add New Row to {{ table_name }}</h1>
        
        <form method="POST">
            {% for column in columns %}
            {% if column != 'id' %}
            <div class="form-group">
                <label for="{{ column }}">{{ column }}:</label>
                {% if column in ['description', 'message', 'admin_response'] %}
                <textarea name="{{ column }}" rows="3"></textarea>
                {% else %}
                <input type="text" name="{{ column }}">
                {% endif %}
            </div>
            {% endif %}
            {% endfor %}
            
            <div class="form-group">
                <button type="submit" class="btn btn-primary">Add Row</button>
                <a href="{{ url_for('view_table', table_name=table_name) }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    print("🌐 Starting Render Database Manager...")
    print("📱 Open your browser and go to: http://localhost:5002")
    print("🔗 Connected to Render PostgreSQL database")
    app.run(debug=True, port=5002)
