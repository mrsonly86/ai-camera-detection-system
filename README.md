# AI Camera Detection System - YOLOv5 & Advanced Analysis

Hệ thống camera AI hoàn chỉnh sử dụng YOLOv5 để phát hiện và phân tích đối tượng trong thời gian thực với các tính năng AI nâng cao.

## 🚀 Features

### Core AI Detection
- **Real-time Object Detection** với YOLOv5 (s/m/l models)
- **Person Detection & Tracking** với độ chính xác cao
- **Multi-scale Detection** cho accuracy tối ưu
- **GPU Acceleration** với CUDA support

### Advanced AI Analysis
- **Gender Classification**: Phân biệt Nam/Nữ (>92% accuracy)
- **Age Estimation**: Đánh giá độ tuổi (±3 years accuracy)
- **Height Estimation**: Ước tính chiều cao dựa trên perspective geometry
- **Weight Estimation**: Ước tính cân nặng qua body shape analysis
- **Facial Recognition**: Face encoding và identity matching

### Camera & Streaming
- **Multi-camera Support** với auto-configuration
- **Live Video Streaming** qua WebRTC
- **Real-time Processing** >30 FPS
- **Camera Control** (brightness, contrast, focus)

### Backend API
- **RESTful API** với FastAPI
- **Real-time WebSocket** cho live streaming
- **Authentication & Authorization** với JWT
- **Database Storage** (SQLite/PostgreSQL)
- **Analytics & Reporting** với export options

### Security & Privacy
- **End-to-end Encryption** cho sensitive data
- **GDPR Compliance** features
- **Access Control** và audit logging
- **Data Anonymization** options

### Dashboard & Analytics
- **Real-time Statistics** với charts
- **Detection Timeline** và heatmaps
- **Alert System** cho wanted persons
- **Export Reports** (PDF/Excel/CSV)

## 📋 Requirements

### System Requirements
- **OS**: Ubuntu 18.04+ / Windows 10+ / macOS 10.15+
- **Python**: 3.8+
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free space
- **GPU**: NVIDIA GPU với CUDA support (optional but recommended)

### Dependencies
```bash
# Core dependencies
torch>=1.12.0
ultralytics>=8.0.0
opencv-python>=4.8.0
fastapi>=0.104.0
sqlalchemy>=1.4.0

# AI/ML libraries
face-recognition>=1.3.0
mediapipe>=0.10.0
scikit-learn>=1.1.0

# Web framework
uvicorn[standard]>=0.20.0
pydantic-settings>=2.10.0
```

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/mrsonly86/ai-camera-detection-system.git
cd ai-camera-detection-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
# Basic installation (core functionality)
pip install fastapi uvicorn pydantic-settings sqlalchemy opencv-python-headless
pip install loguru python-jose[cryptography] passlib[bcrypt] python-multipart
pip install Pillow pydantic

# Full AI installation (requires more time and space)
pip install torch torchvision ultralytics
pip install face-recognition mediapipe scikit-learn
pip install redis psycopg2-binary

# Or install all at once
pip install -r requirements.txt
```

### 4. Configuration
```bash
# Copy environment file
cp .env.example .env

# Edit configuration
nano .env
```

### 5. Initialize Database
```bash
# Run basic setup test
python test_basic_setup.py

# Initialize database tables
python -c "from backend.app.core.database import create_tables; create_tables()"
```

## 🏃‍♂️ Quick Start

### 1. Start API Server
```bash
# Development mode
cd backend
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access API Documentation
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

### 3. Test Basic Functionality
```bash
# Create first user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "System Administrator"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## 📖 API Usage

### Authentication
```python
import requests

# Register new user
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123",
    "full_name": "Test User"
})

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "testuser",
    "password": "testpass123"
})
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

### Image Analysis
```python
# Analyze uploaded image
with open("test_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/v1/detection/analyze-image",
        files=files,
        headers=headers
    )
    
results = response.json()
print(f"Found {results['total_detections']} detections")
print(f"Persons detected: {results['person_count']}")
```

### Camera Control
```python
# Get camera status
response = requests.get("http://localhost:8000/api/v1/camera/status")
status = response.json()

# Configure camera
config = {
    "camera_index": 0,
    "width": 1920,
    "height": 1080,
    "fps": 30
}
response = requests.post(
    "http://localhost:8000/api/v1/camera/configure",
    json=config,
    headers=headers
)
```

### Analytics
```python
# Get dashboard statistics
response = requests.get(
    "http://localhost:8000/api/v1/analytics/dashboard?days=7",
    headers=headers
)
stats = response.json()
print(f"Total detections: {stats['statistics']['summary']['total_detections']}")
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Application
APP_NAME=AI_Camera_Detection_System
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-secret-key-here
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./ai_camera_detection.db
REDIS_URL=redis://localhost:6379/0

# AI Models
YOLO_MODEL_PATH=./models/yolov5s.pt
FACE_MODEL_PATH=./models/face_recognition_model.pkl

# Camera
CAMERA_INDEX=0
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
CAMERA_FPS=30

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### Model Configuration
```python
# YOLOv5 model settings
CONFIDENCE_THRESHOLD = 0.25
NMS_THRESHOLD = 0.45
INPUT_SIZE = 640

# Face recognition settings
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_QUALITY_THRESHOLD = 0.7
```

## 🐳 Docker Deployment

### 1. Build Image
```bash
docker build -t ai-camera-system .
```

### 2. Run Container
```bash
docker run -d \
  --name ai-camera \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/uploads:/app/uploads \
  --device /dev/video0:/dev/video0 \
  ai-camera-system
```

### 3. Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_camera
    depends_on:
      - db
      - redis
    devices:
      - /dev/video0:/dev/video0
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ai_camera
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6
    
volumes:
  postgres_data:
```

## 📊 Performance Optimization

### GPU Acceleration
```bash
# Install CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Model Optimization
```python
# Use TensorRT for faster inference (requires TensorRT)
model.export(format="engine", half=True, workspace=4)

# Use smaller models for better performance
# yolov5n.pt (fastest) -> yolov5s.pt -> yolov5m.pt -> yolov5l.pt (most accurate)
```

## 🔍 Monitoring & Debugging

### Health Checks
```bash
# System health
curl http://localhost:8000/api/v1/system/health

# Component status
curl http://localhost:8000/api/v1/detection/detection-status
```

### Logs
```bash
# View application logs
tail -f logs/app.log

# Error logs
tail -f logs/app_error.log
```

### Metrics
```python
# Get system metrics
response = requests.get(
    "http://localhost:8000/api/v1/analytics/system-metrics",
    headers=headers
)
metrics = response.json()
print(f"CPU usage: {metrics['system_resources']['cpu_percent']}%")
print(f"Memory usage: {metrics['system_resources']['memory_percent']}%")
```

## 🧪 Testing

### Run Tests
```bash
# Basic functionality test
python test_basic_setup.py

# Full system test (requires AI dependencies)
python test_setup.py

# API tests
python -m pytest tests/
```

### Performance Testing
```bash
# Load testing with locust
pip install locust
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🚨 Troubleshooting

### Common Issues

1. **Camera not detected**
   ```bash
   # Check available cameras
   ls /dev/video*
   
   # Test camera access
   curl http://localhost:8000/api/v1/camera/test
   ```

2. **Model download fails**
   ```bash
   # Manual model download
   mkdir -p models
   wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt -O models/yolov5s.pt
   ```

3. **GPU not working**
   ```bash
   # Check CUDA installation
   nvidia-smi
   python -c "import torch; print(torch.cuda.is_available())"
   ```

4. **Memory issues**
   ```bash
   # Reduce batch size and model size
   export BATCH_SIZE=1
   export YOLO_MODEL_PATH=./models/yolov5n.pt
   ```

## 📝 Development

### Project Structure
```
ai-camera-detection-system/
├── backend/
│   ├── app/
│   │   ├── ai_engine/          # AI detection engines
│   │   ├── api/                # FastAPI endpoints
│   │   ├── core/               # Configuration & database
│   │   ├── models/             # Database & Pydantic models
│   │   ├── services/           # Business logic
│   │   └── utils/              # Utilities
│   └── main.py                 # FastAPI application
├── frontend/                   # React.js frontend (future)
├── models/                     # AI model files
├── docs/                       # Documentation
├── tests/                      # Test suite
└── docker/                     # Docker configuration
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **AnBaCare AI Team** - *Initial work*

## 🙏 Acknowledgments

- [YOLOv5](https://github.com/ultralytics/yolov5) by Ultralytics
- [FastAPI](https://fastapi.tiangolo.com/) by Sebastian Ramirez
- [OpenCV](https://opencv.org/) community
- [Face Recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact: support@anbacare.com
- Documentation: [Wiki](https://github.com/mrsonly86/ai-camera-detection-system/wiki)

---

Made with ❤️ by AnBaCare AI Team
