# Subscription Manager

A full-stack web application for managing subscriptions, built with Django and React.

## Prerequisites

- Python 3.8 or higher (Ideally Python 11)
- Node.js 14 or higher
- PostgreSQL 12 or higher
- npm or yarn package manager

## Setup Instructions

### 1. Clone the Repository Thengo to subscription manager

```bash
cd subscription_manager
```

### 2. Set Up Python Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend Dependencies

```bash
# Install Node.js dependencies
npm install
```

### 4. Database Setup

1. Create a PostgreSQL database
2. Update the database credentials in your Django settings
3. Run migrations:
```bash
python manage.py migrate
```

### 5. Environment Variables

Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 6. Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. In a separate terminal, start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Project Structure

- `subscription_manager/` - Main Django project directory
- `frontend/` - React frontend application
- `subscriptions/` - Django app for subscription management
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies

## Development

- Backend API documentation is available at `/api/docs/`
- Frontend components are built with Chakra UI
- The project uses Django REST framework for the API


## License

This project is licensed under the MIT License - see the LICENSE file for details. 