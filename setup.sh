#!/bin/bash

# AI Camera Detection System - Setup Script
# This script sets up the development environment for the AI Camera Detection System

set -e

echo "🚀 AI Camera Detection System - Setup Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Function to check command availability
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        print_status "$1 is installed"
        return 0
    else
        print_warning "$1 is not installed"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install basic dependencies
    print_info "Installing core dependencies..."
    pip install fastapi uvicorn pydantic-settings sqlalchemy opencv-python-headless
    pip install loguru python-jose[cryptography] passlib[bcrypt] python-multipart
    pip install Pillow pydantic python-dotenv
    
    print_status "Core dependencies installed"
    
    # Ask if user wants to install AI dependencies
    read -p "Install AI dependencies (PyTorch, YOLOv5, face-recognition)? This may take several minutes. (y/N): " install_ai
    if [[ $install_ai =~ ^[Yy]$ ]]; then
        print_info "Installing AI dependencies... This may take a while..."
        pip install torch torchvision ultralytics
        pip install face-recognition mediapipe scikit-learn
        print_status "AI dependencies installed"
    else
        print_warning "AI dependencies skipped. Some features will not work."
        print_info "To install later: pip install torch torchvision ultralytics face-recognition mediapipe scikit-learn"
    fi
}

# Function to setup configuration
setup_config() {
    print_info "Setting up configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Created .env file from template"
        
        # Generate secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
        
        # Generate encryption key
        ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        sed -i "s/your-encryption-key-here/$ENCRYPTION_KEY/" .env
        
        print_status "Generated secure keys"
    else
        print_warning ".env file already exists"
    fi
}

# Function to setup database
setup_database() {
    print_info "Setting up database..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Create database tables
    python3 -c "
import sys
sys.path.insert(0, 'backend')
try:
    from backend.app.core.database import create_tables
    create_tables()
    print('✓ Database tables created successfully')
except Exception as e:
    print(f'✗ Database setup failed: {e}')
    sys.exit(1)
    "
    
    print_status "Database initialized"
}

# Function to run tests
run_tests() {
    print_info "Running system tests..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run basic tests
    if python3 test_basic_setup.py; then
        print_status "Basic tests passed"
    else
        print_error "Some tests failed"
        return 1
    fi
}

# Function to create directories
create_directories() {
    print_info "Creating required directories..."
    
    mkdir -p models logs cache uploads
    touch models/.gitkeep logs/.gitkeep cache/.gitkeep uploads/.gitkeep
    
    print_status "Directories created"
}

# Function to download models
download_models() {
    print_info "Checking AI models..."
    
    if [ ! -f "models/yolov5s.pt" ]; then
        read -p "Download YOLOv5s model (~14MB)? (y/N): " download_yolo
        if [[ $download_yolo =~ ^[Yy]$ ]]; then
            print_info "Downloading YOLOv5s model..."
            wget -q --show-progress -O models/yolov5s.pt \
                https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
            print_status "YOLOv5s model downloaded"
        fi
    else
        print_status "YOLOv5s model already exists"
    fi
}

# Function to start development server
start_server() {
    print_info "Starting development server..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if port 8000 is available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
        print_warning "Port 8000 is already in use"
        read -p "Kill existing process and start server? (y/N): " kill_process
        if [[ $kill_process =~ ^[Yy]$ ]]; then
            fuser -k 8000/tcp 2>/dev/null || true
            sleep 2
        else
            print_info "Server not started. Use 'python backend/main.py' to start manually."
            return
        fi
    fi
    
    print_info "Starting server on http://localhost:8000"
    print_info "API documentation: http://localhost:8000/api/v1/docs"
    print_info "Press Ctrl+C to stop the server"
    
    cd backend && python main.py
}

# Main setup function
main() {
    echo
    print_info "Checking system requirements..."
    
    # Check Python
    if ! check_command python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_status "Python $PYTHON_VERSION is compatible"
    else
        print_error "Python 3.8+ is required, found $PYTHON_VERSION"
        exit 1
    fi
    
    # Check pip
    if ! check_command pip3; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check optional dependencies
    check_command git
    check_command wget
    check_command curl
    
    echo
    print_info "System requirements check complete"
    echo
    
    # Run setup steps
    create_directories
    setup_config
    install_python_deps
    setup_database
    download_models
    
    echo
    print_status "Setup completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Review configuration in .env file"
    echo "  2. Start development server: ./setup.sh --start"
    echo "  3. Visit http://localhost:8000/api/v1/docs for API documentation"
    echo "  4. Create your first user via the API"
    echo
    print_info "For production deployment, see docs/DEPLOYMENT.md"
    echo
    
    # Ask if user wants to start server
    read -p "Start development server now? (y/N): " start_now
    if [[ $start_now =~ ^[Yy]$ ]]; then
        echo
        start_server
    fi
}

# Handle command line arguments
case "${1:-}" in
    --start)
        start_server
        ;;
    --test)
        run_tests
        ;;
    --help)
        echo "AI Camera Detection System Setup Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  (no args)  Run full setup"
        echo "  --start    Start development server"
        echo "  --test     Run system tests"
        echo "  --help     Show this help message"
        echo
        ;;
    *)
        main
        ;;
esac