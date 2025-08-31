#!/usr/bin/env python3
"""
Simple Database Manager Web App
View and edit PostgreSQL tables through a web interface
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
import psycopg2
from psycopg2 import sql
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'mymurid_db',
    'user': 'mymurid_user',
    'password': 'mymurid_password_2025',
    'sslmode': 'disable'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def quote_table_name(table_name):
    """Quote table names that are reserved keywords"""
    reserved_keywords = ['order', 'user', 'group', 'table', 'select', 'from', 'where']
    return f'"{table_name}"' if table_name.lower() in reserved_keywords else table_name

@app.route('/')
def index():
    """Show all tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
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
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        # Get table data
        quoted_table_name = quote_table_name(table_name)
        cursor.execute(f"SELECT * FROM {quoted_table_name} LIMIT 100")
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template_string(TABLE_HTML, 
                                   table_name=table_name, 
                                   columns=columns, 
                                   rows=rows)
        
    except Exception as e:
        return f"Error: {e}"

@app.route('/edit/<table_name>/<int:row_id>', methods=['GET', 'POST'])
def edit_row(table_name, row_id):
    """Edit a specific row"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            data = request.form.to_dict()
            
            # Build UPDATE query
            set_clause = ", ".join([f"{k} = %s" for k in data.keys() if k != 'id'])
            values = [v for k, v in data.items() if k != 'id']
            values.append(row_id)
            
            quoted_table_name = quote_table_name(table_name)
            query = f"UPDATE {quoted_table_name} SET {set_clause} WHERE id = %s"
            cursor.execute(query, values)
            conn.commit()
            
            flash(f"Row updated successfully!", "success")
            return redirect(url_for('view_table', table_name=table_name))
        
        # GET: Show edit form
        quoted_table_name = quote_table_name(table_name)
        cursor.execute(f"SELECT * FROM {quoted_table_name} WHERE id = %s", (row_id,))
        row = cursor.fetchone()
        
        # Get column names
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template_string(EDIT_HTML, 
                                   table_name=table_name, 
                                   row=row, 
                                   columns=columns)
        
    except Exception as e:
        return f"Error: {e}"

@app.route('/add/<table_name>', methods=['GET', 'POST'])
def add_row(table_name):
    """Add a new row"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            data = request.form.to_dict()
            
            # Remove empty values
            data = {k: v for k, v in data.items() if v}
            
            # Build INSERT query
            columns = list(data.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            values = list(data.values())
            
            quoted_table_name = quote_table_name(table_name)
            query = f"INSERT INTO {quoted_table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            
            flash(f"Row added successfully!", "success")
            return redirect(url_for('view_table', table_name=table_name))
        
        # GET: Show add form
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template_string(ADD_HTML, 
                                   table_name=table_name, 
                                   columns=columns)
        
    except Exception as e:
        return f"Error: {e}"

@app.route('/delete/<table_name>/<int:row_id>')
def delete_row(table_name, row_id):
    """Delete a row"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        quoted_table_name = quote_table_name(table_name)
        cursor.execute(f"DELETE FROM {quoted_table_name} WHERE id = %s", (row_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash(f"Row deleted successfully!", "success")
        return redirect(url_for('view_table', table_name=table_name))
        
    except Exception as e:
        return f"Error: {e}"

# HTML Templates
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MyMurid Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .table-list { margin: 20px 0; }
        .table-item { 
            padding: 10px; margin: 5px 0; 
            background: #f0f0f0; border-radius: 5px;
            text-decoration: none; color: #333; display: block;
        }
        .table-item:hover { background: #e0e0e0; }
        h1 { color: #2c3e50; }
    </style>
</head>
<body>
    <h1>🐘 MyMurid Database Manager</h1>
    <p>Click on a table to view and edit its contents:</p>
    
    <div class="table-list">
        {% for table in tables %}
        <a href="/table/{{ table[0] }}" class="table-item">
            📋 {{ table[0] }}
        </a>
        {% endfor %}
    </div>
    
    <p><small>This is a simple database manager for viewing and editing your PostgreSQL tables.</small></p>
</body>
</html>
"""

TABLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ table_name }} - Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .actions { margin: 10px 0; }
        .btn { padding: 5px 10px; margin: 2px; text-decoration: none; border-radius: 3px; }
        .btn-edit { background: #3498db; color: white; }
        .btn-delete { background: #e74c3c; color: white; }
        .btn-add { background: #27ae60; color: white; }
        .back-link { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="back-link">
        <a href="/">← Back to Tables</a>
    </div>
    
    <h1>📋 Table: {{ table_name }}</h1>
    
    <div class="actions">
        <a href="/add/{{ table_name }}" class="btn btn-add">➕ Add New Row</a>
    </div>
    
    <table>
        <thead>
            <tr>
                {% for col in columns %}
                <th>{{ col[0] }} ({{ col[1] }})</th>
                {% endfor %}
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                {% for cell in row %}
                <td>{{ cell }}</td>
                {% endfor %}
                <td>
                    <a href="/edit/{{ table_name }}/{{ row[0] }}" class="btn btn-edit">✏️ Edit</a>
                    <a href="/delete/{{ table_name }}/{{ row[0] }}" class="btn btn-delete" 
                       onclick="return confirm('Are you sure you want to delete this row?')">🗑️ Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <p><small>Showing up to 100 rows. Use pgAdmin for full database management.</small></p>
</body>
</html>
"""

EDIT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Row - Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
        .btn { padding: 10px 20px; margin: 10px 5px; border: none; border-radius: 3px; cursor: pointer; }
        .btn-primary { background: #3498db; color: white; }
        .btn-secondary { background: #95a5a6; color: white; }
    </style>
</head>
<body>
    <h1>✏️ Edit Row in {{ table_name }}</h1>
    
    <form method="POST">
        {% for i, col in enumerate(columns) %}
        <div class="form-group">
            <label for="{{ col[0] }}">{{ col[0] }} ({{ col[1] }})</label>
            {% if col[1] == 'text' %}
            <textarea name="{{ col[0] }}" id="{{ col[0] }}">{{ row[i] or '' }}</textarea>
            {% else %}
            <input type="text" name="{{ col[0] }}" id="{{ col[0] }}" value="{{ row[i] or '' }}">
            {% endif %}
        </div>
        {% endfor %}
        
        <button type="submit" class="btn btn-primary">💾 Save Changes</button>
        <a href="/table/{{ table_name }}" class="btn btn-secondary">❌ Cancel</a>
    </form>
</body>
</html>
"""

ADD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Row - Database Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
        .btn { padding: 10px 20px; margin: 10px 5px; border: none; border-radius: 3px; cursor: pointer; }
        .btn-primary { background: #27ae60; color: white; }
        .btn-secondary { background: #95a5a6; color: white; }
    </style>
</head>
<body>
    <h1>➕ Add New Row to {{ table_name }}</h1>
    
    <form method="POST">
        {% for col in columns %}
        {% if col[0] != 'id' and col[0] != 'created_at' %}
        <div class="form-group">
            <label for="{{ col[0] }}">{{ col[0] }} ({{ col[1] }})</label>
            {% if col[1] == 'text' %}
            <textarea name="{{ col[0] }}" id="{{ col[0] }}"></textarea>
            {% else %}
            <input type="text" name="{{ col[0] }}" id="{{ col[0] }}" value="">
            {% endif %}
        </div>
        {% endif %}
        {% endfor %}
        
        <button type="submit" class="btn btn-primary">➕ Add Row</button>
        <a href="/table/{{ table_name }}" class="btn btn-secondary">❌ Cancel</a>
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    print("🌐 Starting Database Manager...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("🔗 Your main app is still running at: http://localhost:5000")
    app.run(debug=True, port=5001)
