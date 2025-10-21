# 🔧 GemCart Backend API

Flask-based REST API for the GemCart jewelry e-commerce platform.

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python app.py
```

**API Base URL**: http://localhost:5000

## 📋 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Products
- `GET /api/products` - List all products
- `GET /api/products/:id` - Get product details
- `GET /api/products/categories` - Get categories

### Orders (TODO)
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders

## 🗄️ Database Models
- **User**: Authentication and profile
- **Product**: Jewelry items
- **Category**: Product categories
- **Order**: Purchase orders (TODO)

## 🔑 Environment Variables
```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///gemcart.db
```

## 📁 Project Structure
```
backend/
├── app.py              # Main Flask application
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── routes/            # API endpoints
│   ├── auth.py        # Authentication routes
│   └── products.py    # Product routes
└── instance/          # Database files
```

## 🧪 Testing
```bash
python -m pytest
```

