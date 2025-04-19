# Subscription Manager

A full-stack web application for managing subscriptions, built with Django and React.

# Trello Board
https://trello.com/b/iACNBQCT/subman


## Prerequisites

- Python 3.8 or higher (Ideally Python 11)
- Node.js 14 or higher
- PostgreSQL 12 or higher
- npm or yarn package manager
- Redis (for Celery task queue)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
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

### 5. Redis Setup

1. Install Redis:
   - **macOS**: `brew install redis`
   - **Ubuntu/Debian**: `sudo apt-get install redis-server`
   - **Windows**: Download from https://redis.io/download

2. Start Redis server:
   - **macOS**: `brew services start redis`
   - **Ubuntu/Debian**: `sudo service redis-server start`
   - **Windows**: Run the Redis server executable

### 6. Environment Variables

Create a `.env` file in the root directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 7. Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. In a separate terminal, start the frontend development server:
```bash
cd frontend
npm start
```

3. Start Celery worker (in a new terminal):
```bash
celery -A subscription_manager worker -l info
```

4. Start Celery beat scheduler (in a new terminal):
```bash
celery -A subscription_manager beat -l info
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

## Features

- User authentication and authorization
- Subscription management (create, read, update, delete)
- Email notifications for upcoming subscription renewals
- Background task processing with Celery
- RESTful API with Django REST framework
- Modern UI with Chakra UI

## Development

- Backend API documentation is available at `/api/docs/`
- Frontend components are built with Chakra UI
- The project uses Django REST framework for the API
- Email notifications are sent using Django's email backend
- Background tasks are handled by Celery with Redis as the message broker

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Current Issues and Improvements
- Extract cancellation date correctly ✅
- Fixing total cost calculation ✅
- When editing in the restore Page, and i cancel, it should go back to the cancel dashboard ✅
- Direct to login page when starting the operation ✅
- When Free Trial becomes Paid Subscription 

- Sending email for reminder 
    - Successfully create the email reminder task. (After)
    - Successfully cancel the email reminder task when I choose not to use reminder when editing a subscription.
    - Successfully cancel the email reminder task when I remove subscription.

- Have a settings page (reset password, view email and personal info in registration ) Choose default themes etc.

- Correctly set up registration process  (email verification)
- Set up CICD pipeline
- Deploy