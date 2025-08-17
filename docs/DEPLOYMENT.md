# Deployment Guide - AI Camera Detection System

## Overview

This guide covers different deployment scenarios for the AI Camera Detection System, from development to production environments.

## Prerequisites

- Docker & Docker Compose
- Git
- Python 3.8+ (for local development)
- NVIDIA Docker (for GPU support)

## Development Deployment

### Local Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/mrsonly86/ai-camera-detection-system.git
cd ai-camera-detection-system
```

2. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

3. **Configuration**
```bash
cp .env.example .env
# Edit .env file with your settings
nano .env
```

4. **Database Setup**
```bash
python -c "from backend.app.core.database import create_tables; create_tables()"
```

5. **Run Development Server**
```bash
cd backend
python main.py
```

## Production Deployment

### Docker Deployment (Recommended)

#### Single Machine Deployment

1. **Prepare Environment**
```bash
# Clone repository
git clone https://github.com/mrsonly86/ai-camera-detection-system.git
cd ai-camera-detection-system

# Create production environment file
cp .env.example .env
nano .env
```

2. **Production Configuration (.env)**
```bash
# Application
APP_NAME=AI_Camera_Detection_System
DEBUG=false
SECRET_KEY=your-very-secure-secret-key-here
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://ai_camera_user:secure_password@db:5432/ai_camera_db
REDIS_URL=redis://redis:6379/0

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your-encryption-key-32-characters

# Performance
MAX_WORKERS=4
BATCH_SIZE=8
GPU_ENABLED=true
```

3. **Build and Deploy**
```bash
# Build images
docker-compose build

# Deploy services
docker-compose up -d

# Check status
docker-compose ps
```

4. **Initialize Application**
```bash
# Create database tables
docker-compose exec api python -c "from backend.app.core.database import create_tables; create_tables()"

# Create admin user
docker-compose exec api python -c "
from backend.app.core.database import SessionLocal
from backend.app.services.user_service import UserService
from backend.app.models.schemas import UserCreate

db = SessionLocal()
user_service = UserService(db)
admin_user = UserCreate(
    username='admin',
    email='admin@example.com',
    password='admin123',
    full_name='System Administrator'
)
user_service.create_user(admin_user)
db.close()
print('Admin user created')
"
```

### GPU Support

For GPU-accelerated inference:

1. **Install NVIDIA Docker**
```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

2. **Update Docker Compose**
```yaml
# Add to api service in docker-compose.yml
services:
  api:
    # ... existing config
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Cloud Deployment

#### AWS Deployment

1. **EC2 Instance Setup**
```bash
# Launch EC2 instance (recommended: g4dn.xlarge for GPU)
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Load Balancer Setup**
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name ai-camera-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Create target group
aws elbv2 create-target-group \
  --name ai-camera-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345678
```

3. **RDS Database**
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier ai-camera-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username ai_camera_user \
  --master-user-password securepassword \
  --allocated-storage 20
```

#### Google Cloud Platform

1. **GKE Deployment**
```bash
# Create GKE cluster
gcloud container clusters create ai-camera-cluster \
  --zone=us-central1-a \
  --node-locations=us-central1-a \
  --num-nodes=2 \
  --machine-type=n1-standard-2

# Get credentials
gcloud container clusters get-credentials ai-camera-cluster --zone=us-central1-a
```

2. **Kubernetes Manifests**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-camera-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-camera-api
  template:
    metadata:
      labels:
        app: ai-camera-api
    spec:
      containers:
      - name: api
        image: gcr.io/PROJECT_ID/ai-camera:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

#### Azure Deployment

1. **Container Instances**
```bash
# Create resource group
az group create --name ai-camera-rg --location eastus

# Create container instance
az container create \
  --resource-group ai-camera-rg \
  --name ai-camera-api \
  --image your-registry/ai-camera:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL="postgresql://..." \
    REDIS_URL="redis://..."
```

## High Availability Setup

### Multi-Node Deployment

1. **Docker Swarm Setup**
```bash
# Initialize swarm on manager node
docker swarm init --advertise-addr MANAGER_IP

# Join worker nodes
docker swarm join --token TOKEN MANAGER_IP:2377
```

2. **Deploy Stack**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: ai-camera:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

3. **Deploy Services**
```bash
docker stack deploy -c docker-compose.prod.yml ai-camera
```

### Load Balancing

#### Nginx Load Balancer
```nginx
upstream api_backend {
    least_conn;
    server api1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server api2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server api3:8000 weight=1 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### HAProxy Configuration
```
global
    daemon

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend api_frontend
    bind *:80
    default_backend api_backend

backend api_backend
    balance roundrobin
    option httpchk GET /health
    server api1 api1:8000 check
    server api2 api2:8000 check
    server api3 api3:8000 check
```

## Database Setup

### PostgreSQL Configuration

1. **Production Database**
```sql
-- Create database and user
CREATE DATABASE ai_camera_db;
CREATE USER ai_camera_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_camera_db TO ai_camera_user;

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
```

2. **Backup Strategy**
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="ai_camera_db"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U ai_camera_user $DB_NAME > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Redis Configuration

```redis
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## Security Configuration

### SSL/TLS Setup

1. **Let's Encrypt Certificate**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

2. **Nginx SSL Configuration**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
}
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Monitoring & Logging

### Prometheus Metrics
```python
# Add to FastAPI app
from prometheus_client import Counter, Histogram, generate_latest

REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
RESPONSE_TIME = Histogram('http_response_time_seconds', 'HTTP response time')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    RESPONSE_TIME.observe(process_time)
    
    return response
```

### Log Aggregation
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:7.17.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:7.17.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## Performance Optimization

### Application Performance

1. **Connection Pooling**
```python
# Database connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300
)
```

2. **Caching Strategy**
```python
# Redis caching
@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    if request.method == "GET":
        cache_key = f"cache:{request.url}"
        cached = await redis.get(cache_key)
        if cached:
            return JSONResponse(json.loads(cached))
    
    response = await call_next(request)
    
    if request.method == "GET" and response.status_code == 200:
        await redis.setex(cache_key, 300, response.body)
    
    return response
```

### Infrastructure Scaling

1. **Auto Scaling (AWS)**
```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name ai-camera-asg \
  --launch-template LaunchTemplateName=ai-camera-template \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --target-group-arns arn:aws:elasticloadbalancing:...
```

2. **Horizontal Pod Autoscaling (K8s)**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-camera-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-camera-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check database connectivity
docker-compose exec api python -c "
from backend.app.core.database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database connected successfully')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

2. **Memory Issues**
```bash
# Monitor memory usage
docker stats
free -h
# Adjust model batch size or use smaller models
```

3. **GPU Issues**
```bash
# Check GPU availability
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Log Analysis

```bash
# Application logs
docker-compose logs -f api

# Database logs
docker-compose logs -f db

# System logs
journalctl -u docker.service
```

## Backup & Recovery

### Database Backup
```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U ai_camera_user ai_camera_db > backup_$TIMESTAMP.sql
aws s3 cp backup_$TIMESTAMP.sql s3://your-backup-bucket/
```

### Full System Backup
```bash
# Backup volumes and configuration
docker-compose down
tar -czf backup_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env \
  models/ \
  uploads/ \
  logs/
```

### Disaster Recovery
```bash
# Restore from backup
tar -xzf backup_20240101.tar.gz
docker-compose up -d db redis
sleep 30
docker-compose exec -T db psql -U ai_camera_user ai_camera_db < backup_20240101.sql
docker-compose up -d
```