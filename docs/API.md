# API Documentation - AI Camera Detection System

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints (except health checks and system info) require authentication using JWT tokens.

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user123&password=securepassword
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Authentication Token
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Detection Endpoints

### Create Detection Session
```http
POST /detection/session
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_name": "Living Room Monitoring",
  "camera_settings": {
    "camera_index": 0,
    "width": 1920,
    "height": 1080,
    "fps": 30
  }
}
```

### Analyze Image
```http
POST /detection/analyze-image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>
session_id: 123 (optional)
```

Response:
```json
{
  "filename": "test.jpg",
  "detections": [
    {
      "object_class": "person",
      "confidence": 0.85,
      "bbox": {
        "x1": 100,
        "y1": 50,
        "x2": 300,
        "y2": 400
      },
      "gender": "male",
      "gender_confidence": 0.92,
      "estimated_age": 28,
      "age_confidence": 0.78,
      "estimated_height": 175.5,
      "estimated_weight": 70.2,
      "face_match": {
        "matched": false,
        "name": "unknown",
        "confidence": 0.0
      }
    }
  ],
  "total_detections": 1,
  "person_count": 1
}
```

### Live Stream
```http
GET /detection/live-stream
```

Returns a multipart MJPEG stream with detection overlays.

### Start Live Detection
```http
POST /detection/start-live-detection
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": 123
}
```

### Stop Live Detection
```http
POST /detection/stop-live-detection
Authorization: Bearer <token>
```

## Camera Control

### Get Camera Info
```http
GET /camera/info
Authorization: Bearer <token>
```

### Configure Camera
```http
POST /camera/configure
Authorization: Bearer <token>
Content-Type: application/json

{
  "camera_index": 0,
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "brightness": 0.5,
  "contrast": 1.0,
  "saturation": 1.0
}
```

### Test Camera
```http
POST /camera/test
Authorization: Bearer <token>
```

### Camera Status
```http
GET /camera/status
```

## Face Recognition

### Add Known Person
```http
POST /face/known-persons
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "description": "Employee #12345",
  "national_id": "ID123456789",
  "nationality": "Vietnamese",
  "is_wanted": false,
  "risk_level": "low"
}
```

### Add Face to Person
```http
POST /face/known-persons/{person_id}/add-face
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <face_image>
```

### Recognize Face
```http
POST /face/recognize
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <face_image>
```

Response:
```json
{
  "recognition_result": {
    "matched": true,
    "name": "John Doe",
    "confidence": 0.85,
    "distance": 0.15,
    "metadata": {
      "id": 1,
      "is_wanted": false,
      "risk_level": "low"
    }
  },
  "face_quality": {
    "sharpness": 0.8,
    "brightness": 0.7,
    "contrast": 0.9,
    "overall": 0.8
  }
}
```

### Get Known Persons
```http
GET /face/known-persons
Authorization: Bearer <token>
```

## Analytics

### Dashboard Statistics
```http
GET /analytics/dashboard?days=7
Authorization: Bearer <token>
```

Response:
```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-01-08T00:00:00",
    "days": 7
  },
  "statistics": {
    "summary": {
      "total_sessions": 5,
      "total_detections": 150,
      "person_detections": 120,
      "alert_count": 3,
      "detection_rate": 30.0
    },
    "gender_distribution": {
      "male": 70,
      "female": 45,
      "unknown": 5
    },
    "age_statistics": {
      "average_age": 32.5,
      "min_age": 18,
      "max_age": 65
    }
  }
}
```

### Detection Timeline
```http
GET /analytics/detection-timeline?hours=24
Authorization: Bearer <token>
```

### Gender Distribution
```http
GET /analytics/gender-distribution?days=7
Authorization: Bearer <token>
```

### Age Distribution
```http
GET /analytics/age-distribution?days=7
Authorization: Bearer <token>
```

### Export Data
```http
GET /analytics/export-data?format=json&days=30
Authorization: Bearer <token>
```

## System Management

### System Information
```http
GET /system/info
```

Response:
```json
{
  "application": {
    "name": "AI Camera Detection System",
    "version": "1.0.0",
    "debug": false
  },
  "system": {
    "platform": "Linux",
    "python_version": "3.11.0"
  },
  "ai_libraries": {
    "pytorch_version": "2.0.0",
    "cuda_available": true,
    "opencv_version": "4.8.0"
  },
  "gpu_info": {
    "cuda_available": true,
    "gpu_count": 1,
    "gpu_name": "NVIDIA GeForce RTX 3080"
  }
}
```

### Health Check
```http
GET /system/health
```

### System Configuration
```http
GET /system/config
Authorization: Bearer <token>
```

### Update Configuration
```http
PUT /system/config/{config_key}
Authorization: Bearer <token>
Content-Type: application/json

{
  "config_value": "0.8",
  "description": "Face recognition threshold"
}
```

### System Logs
```http
GET /system/logs?lines=100
Authorization: Bearer <token>
```

## Error Responses

All API endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

- General API: 10 requests/second
- File upload: 2 requests/second
- Live streaming: No limit

## WebSocket Endpoints

### Real-time Notifications
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Notification:', data);
};
```

### Live Detection Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/detection');
ws.onmessage = function(event) {
    const detection = JSON.parse(event.data);
    console.log('New detection:', detection);
};
```

## SDKs and Libraries

### Python SDK
```python
import requests
from ai_camera_sdk import CameraClient

client = CameraClient(base_url="http://localhost:8000/api/v1")
client.login("username", "password")

# Analyze image
result = client.analyze_image("path/to/image.jpg")
print(f"Found {len(result.detections)} objects")

# Start live detection
session = client.create_session("My Session")
client.start_live_detection(session.id)
```

### JavaScript SDK
```javascript
import { CameraAPI } from 'ai-camera-sdk';

const api = new CameraAPI('http://localhost:8000/api/v1');
await api.login('username', 'password');

// Analyze image
const result = await api.analyzeImage(imageFile);
console.log(`Found ${result.detections.length} objects`);

// Real-time notifications
api.onDetection((detection) => {
    console.log('New detection:', detection);
});
```