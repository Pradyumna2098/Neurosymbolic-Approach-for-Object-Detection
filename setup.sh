#!/bin/bash

# Setup script for Neurosymbolic Object Detection repository
# This script helps set up the development environment

set -e

echo "=========================================="
echo "Neurosymbolic Object Detection Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi
echo "✅ Python $(python3 --version) found"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. Docker is recommended for easy deployment."
else
    echo "✅ Docker $(docker --version) found"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Required for frontend development."
else
    echo "✅ Node.js $(node --version) found"
fi

echo ""
echo "Choose setup option:"
echo "1) Full Docker setup (recommended)"
echo "2) Local development setup"
echo "3) Backend only"
echo "4) Frontend only"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Setting up with Docker Compose..."
        if ! command -v docker-compose &> /dev/null; then
            echo "❌ docker-compose is not installed."
            exit 1
        fi
        
        echo "Building and starting all services..."
        docker-compose up -d --build
        
        echo ""
        echo "=========================================="
        echo "✅ Setup complete!"
        echo "=========================================="
        echo ""
        echo "Services are now running:"
        echo "  - Frontend:   http://localhost:3000"
        echo "  - Backend:    http://localhost:8000"
        echo "  - API Docs:   http://localhost:8000/docs"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana:    http://localhost:3001 (admin/admin)"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop:      docker-compose down"
        ;;
    
    2)
        echo ""
        echo "Setting up local development environment..."
        
        # Create virtual environment
        echo "Creating Python virtual environment..."
        python3 -m venv .venv
        
        echo "Activating virtual environment..."
        source .venv/bin/activate || . .venv/Scripts/activate
        
        # Install system dependencies
        echo "Installing system dependencies..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y swi-prolog
        else
            echo "⚠️  Please manually install swi-prolog for your system"
        fi
        
        # Install Python dependencies
        echo "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov
        
        # Install frontend dependencies
        echo "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
        
        echo ""
        echo "=========================================="
        echo "✅ Setup complete!"
        echo "=========================================="
        echo ""
        echo "To start backend:"
        echo "  cd backend && uvicorn app.main:app --reload"
        echo ""
        echo "To start frontend:"
        echo "  cd frontend && npm start"
        echo ""
        echo "To run tests:"
        echo "  pytest tests/"
        ;;
    
    3)
        echo ""
        echo "Setting up backend only..."
        
        # Create virtual environment
        python3 -m venv .venv
        source .venv/bin/activate || . .venv/Scripts/activate
        
        # Install dependencies
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r backend/requirements.txt
        
        echo ""
        echo "=========================================="
        echo "✅ Backend setup complete!"
        echo "=========================================="
        echo ""
        echo "To start backend:"
        echo "  cd backend && uvicorn app.main:app --reload"
        ;;
    
    4)
        echo ""
        echo "Setting up frontend only..."
        
        cd frontend
        npm install
        cd ..
        
        echo ""
        echo "=========================================="
        echo "✅ Frontend setup complete!"
        echo "=========================================="
        echo ""
        echo "To start frontend:"
        echo "  cd frontend && npm start"
        ;;
    
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
