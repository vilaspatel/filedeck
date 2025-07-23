#!/bin/bash

# Content Manager Development Setup Script

set -e

echo "🚀 Setting up Content Manager for development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed. You may need it for local development."
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 is not installed. You may need it for local development."
fi

print_status "Creating environment files..."

# Create backend .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    print_status "Creating backend/.env from template..."
    cat > backend/.env << EOF
# Development Environment Configuration
APP_NAME=Content Manager
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key-change-in-production

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Database Configuration
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://contentmanager:changeme@localhost:5432/contentmanager

# Storage Configuration
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads

# Azure AD Configuration (replace with your values)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CORS_ALLOW_CREDENTIALS=true

# Multi-tenancy
ENABLE_MULTI_TENANCY=true
DEFAULT_TENANT_ID=default

# Security
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload Configuration
MAX_FILE_SIZE=100
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,xml,json,csv,xlsx,png,jpg,jpeg,gif
CHUNK_SIZE=8192

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF
else
    print_status "backend/.env already exists, skipping..."
fi

# Create frontend .env file if it doesn't exist
if [ ! -f frontend/.env ]; then
    print_status "Creating frontend/.env from template..."
    cat > frontend/.env << EOF
# Development Environment Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Azure AD Configuration (replace with your values)
REACT_APP_AZURE_CLIENT_ID=your-azure-client-id
REACT_APP_AZURE_TENANT_ID=your-azure-tenant-id
REACT_APP_AZURE_AUTHORITY=https://login.microsoftonline.com/your-azure-tenant-id
REACT_APP_REDIRECT_URI=http://localhost:3000

# Application Configuration
REACT_APP_VERSION=1.0.0
REACT_APP_APP_NAME=Content Manager

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUGGING=true
EOF
else
    print_status "frontend/.env already exists, skipping..."
fi

# Create uploads directory
print_status "Creating uploads directory..."
mkdir -p backend/uploads

# Install backend dependencies
if [ "$1" == "--install-deps" ]; then
    print_status "Installing backend dependencies..."
    cd backend
    python3 -m pip install --user -r requirements.txt
    cd ..

    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

print_status "Starting development environment with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_status "✅ Development environment is ready!"
    echo
    echo "📋 Service URLs:"
    echo "   🖥️  Frontend:  http://localhost:3000"
    echo "   🔧 Backend:   http://localhost:8000"
    echo "   📊 API Docs:  http://localhost:8000/docs"
    echo "   🗄️  Database: postgresql://contentmanager:changeme@localhost:5432/contentmanager"
    echo
    echo "🔧 Useful commands:"
    echo "   📜 View logs:     docker-compose logs -f"
    echo "   🛑 Stop:          docker-compose down"
    echo "   🔄 Restart:       docker-compose restart"
    echo "   🧹 Clean up:      docker-compose down -v"
    echo
    print_warning "Don't forget to:"
    echo "   1. Configure your Azure AD application"
    echo "   2. Update the .env files with your actual values"
    echo "   3. Set up your storage accounts if using cloud storage"
else
    print_error "❌ Failed to start development environment"
    print_error "Check the logs with: docker-compose logs"
    exit 1
fi 