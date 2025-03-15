#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Subscription Manager Project${NC}"
echo "======================================"

# Check if PostgreSQL is installed
echo -e "\n${YELLOW}Checking PostgreSQL installation...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL is not installed.${NC}"
    echo "Installing PostgreSQL..."
    brew install postgresql
    
    echo "Starting PostgreSQL service..."
    brew services start postgresql
else
    echo -e "${GREEN}PostgreSQL is already installed.${NC}"
    echo "Ensuring PostgreSQL service is running..."
    brew services start postgresql
fi

# Wait for PostgreSQL to start
echo "Waiting for PostgreSQL to start..."
sleep 3

# Check Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install psycopg2-binary django djangorestframework django-cors-headers djangorestframework-simplejwt

# Check PostgreSQL connection
echo -e "\n${YELLOW}Checking PostgreSQL connection...${NC}"
python check_postgres.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to connect to PostgreSQL. Please check the error message above.${NC}"
    exit 1
fi

# Run Django migrations
echo -e "\n${YELLOW}Running Django migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

# Check if superuser exists
echo -e "\n${YELLOW}Checking if superuser exists...${NC}"
python -c "from django.contrib.auth.models import User; print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')"

# Create superuser if needed
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install
npm install @chakra-ui/icons

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To start the backend:${NC}"
echo "cd /Users/peterhuang/Desktop/Code\ example/subscription_manager"
echo "python manage.py runserver"
echo -e "${YELLOW}To start the frontend:${NC}"
echo "cd /Users/peterhuang/Desktop/Code\ example/subscription_manager/frontend"
echo "npm start" 