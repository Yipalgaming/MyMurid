# 🍽️ MyMurid - School Canteen & Co-op Management System

A comprehensive digital solution for school canteens and cooperatives, featuring pre-ordering, digital payments, and cashless transactions.

## ✨ Features

### 🎯 Core Functionality
- **Pre-Ordering System** - Students order food in advance
- **Digital Wallet** - Cashless payment with student balance
- **Role-Based Access** - Students, Teachers, and Admin roles
- **Barcode Authentication** - IC card-based login system
- **Real-Time Order Tracking** - Monitor order status

### 👥 User Roles
- **Students** - Order food, manage balance, vote on menu items
- **Teachers/Staff** - Process orders, manage kitchen operations
- **Administrators** - Manage students, monitor finances, handle top-ups

### 🍽️ Menu & Ordering
- **Categorized Menu** - Food items with images and descriptions
- **Shopping Cart** - Easy item selection and quantity management
- **Order Management** - Track pending, paid, and completed orders
- **Payment Processing** - Secure digital wallet transactions

### 📊 Management Features
- **Student Management** - Balance tracking, card freezing
- **Transaction History** - Complete financial records
- **Voting System** - Student feedback on menu preferences
- **Feedback Collection** - Continuous improvement system

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Canteen-Kiosk
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   ```bash
   python setup_db.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the system**
   - Open your browser and go to: `http://localhost:5000`
   - Use the sample credentials below to test

## 🔑 Sample Login Credentials

### Students
- **Ahmad bin Ali**
  - IC: `1234`
  - PIN: `1234`
  - Balance: RM 50

- **Sean Chuah Shang En**
  - IC: `5678`
  - PIN: `5678`
  - Balance: RM 25

### Administrator
- **Admin Teacher**
  - IC: `9999`
  - PIN: `9999`
  - Password: `admin123`

## 🗄️ Database Setup

### Current Setup: SQLite (Development)
- Database file: `instance/database.db`
- Automatic setup with sample data
- No additional configuration needed

### Future: PostgreSQL (Production)
- Set environment variable: `DATABASE_URL`
- Example: `postgresql://username:password@localhost:5432/mymurid`
- Run: `flask db upgrade` to migrate

## 📁 Project Structure

```
Canteen-Kiosk/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── config.py             # Configuration settings
├── setup_db.py           # Database setup script
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── migrations/          # Database migrations
└── instance/            # Database files
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Flask Environment
FLASK_ENV=development

# Secret Key (change in production!)
SECRET_KEY=your-super-secret-key-here

# Database (for PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost:5432/mymurid
```

### Database Configuration
The system automatically detects your database setup:
- **Development**: Uses SQLite (no setup required)
- **Production**: Set `DATABASE_URL` for PostgreSQL

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (Heroku)
1. Create a new Heroku app
2. Add PostgreSQL addon
3. Set environment variables
4. Deploy with Git

### Production (Other Platforms)
- Set `FLASK_ENV=production`
- Configure `DATABASE_URL`
- Set `SECRET_KEY`
- Use production WSGI server (Gunicorn)

## 🎯 Future Features

### 🗺️ Directory Map System
- Interactive school directory
- Teacher/room location search
- Admin location management

### 💝 Donation System
- Student/parent donations
- Transparent reporting
- Transaction tracking

### 🎁 Reward System ("Trash to Cash")
- Eco-action points
- Recycling rewards
- Canteen vouchers

### 📰 News Hub
- School announcements
- Event updates
- Rich media support

### 📱 Mobile Integration
- Flutter mobile app
- Push notifications
- QR code scanning

## 🛠️ Development

### Database Migrations
```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Check current status
flask db current
```

### Adding New Features
1. Update models in `models.py`
2. Create database migration
3. Add routes in `app.py`
4. Create HTML templates
5. Test functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or support:
- Check the documentation
- Review existing issues
- Create a new issue with details

## 📄 License

This project is developed for educational purposes and school management.

---

**Built with ❤️ for modernizing school canteen operations**
