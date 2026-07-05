# Online Calculator - AWS Elastic Beanstalk Application

A modern, responsive online calculator web application built with Python Flask, featuring real-time calculations and persistent storage of calculation history in PostgreSQL. Designed to be deployed on AWS Elastic Beanstalk with complete infrastructure as code.

## 🚀 Features

### Core Functionality
- **Real-time Calculator**: Perform mathematical operations instantly
- **Expression Support**: Full support for +, -, *, /, parentheses, and complex expressions
- **Calculation History**: All calculations are saved to the database
- **Statistics Dashboard**: View total calculations, averages, min/max values
- **Delete Operations**: Remove individual calculations from history

### Technical Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **REST API**: Full REST API for all operations
- **Database Integration**: PostgreSQL for persistent data storage
- **Health Monitoring**: Built-in health check endpoints
- **Auto-Scaling**: Automatic scaling based on CPU utilization
- **CloudWatch Logging**: Comprehensive application and infrastructure logging

## 📋 Prerequisites

- Python 3.8+
- Docker & Docker Compose (for local development)
- AWS Account with appropriate permissions
- AWS CLI and EB CLI installed
- Git

## 🏃 Quick Start - Local Development

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd calculator-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run with Docker Compose

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# Access application
# Browser: http://localhost:5000
# API: http://localhost:5000/api/calculate
```

### 3. Test the Application

```bash
# Test health check
curl http://localhost:5000/health

# Test calculation
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "10 + 5 * 2"}'

# Get history
curl http://localhost:5000/api/history

# Get statistics
curl http://localhost:5000/api/statistics
```

### 4. Stop Services

```bash
docker-compose down
```

## 🚢 AWS Elastic Beanstalk Deployment

### 1. Prerequisites

```bash
# Install AWS CLI
pip install awscli

# Install EB CLI
pip install awsebcli

# Configure AWS credentials
aws configure
```

### 2. Initialize Elastic Beanstalk

```bash
# In project directory
eb init -p python-3.11 calculator-app --region us-east-1
```

### 3. Create Environment

```bash
# Create development environment
eb create calculator-dev \
  --instance-type t3.micro \
  --envvars RDS_PASSWORD=your-secure-password

# Wait for creation (5-10 minutes)
eb status
```

### 4. Deploy Application

```bash
# Deploy
eb deploy

# Check status
eb status

# Open in browser
eb open
```

### 5. Monitor Application

```bash
# View logs
eb logs --stream

# View health
eb health

# View events
eb events --follow
```

## 📁 Project Structure

```
calculator-app/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Local development setup
├── .ebignore                       # Files to ignore in EB
├── .env.example                    # Environment template
├── README.md                       # This file
├── DEPLOYMENT_GUIDE.md             # Detailed deployment guide
├── templates/
│   └── index.html                  # Web interface
├── static/                         # Static files (CSS, JS)
└── .ebextensions/
    ├── 01_python.config            # Python configuration
    ├── 02_rds.config               # Database configuration
    └── 03_healthcheck.config       # Health check & scaling
```

## 🔧 API Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy", "database": "connected"}
```

### Calculate
```
POST /api/calculate
Body: {"expression": "10 + 5 * 2"}
Response: {"expression": "10 + 5 * 2", "result": 20, "id": 1}
```

### Get History
```
GET /api/history?limit=20
Response: [
  {
    "id": 1,
    "expression": "10 + 5",
    "result": 15,
    "timestamp": "2026-07-05T12:00:00",
    "user_ip": "192.168.1.1"
  },
  ...
]
```

### Delete Calculation
```
DELETE /api/history/{id}
Response: {"message": "Calculation deleted"}
```

### Get Statistics
```
GET /api/statistics
Response: {
  "total_calculations": 50,
  "average_result": 25.5,
  "min_result": 1.0,
  "max_result": 100.0
}
```

## 🗄️ Database Schema

### Calculations Table
```sql
CREATE TABLE calculations (
  id SERIAL PRIMARY KEY,
  expression VARCHAR(255) NOT NULL,
  result FLOAT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_ip VARCHAR(45)
);
```

## 🔐 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RDS_HOSTNAME` | Database host | `mydb.123456.us-east-1.rds.amazonaws.com` |
| `RDS_PORT` | Database port | `5432` |
| `RDS_DB_NAME` | Database name | `calculator_db` |
| `RDS_USERNAME` | Database user | `admin` |
| `RDS_PASSWORD` | Database password | `your-secure-password` |
| `FLASK_ENV` | Environment | `production` |

## 📊 Monitoring & Logging

### CloudWatch Logs
```bash
# View logs
eb logs

# Stream logs in real-time
eb logs --stream

# View in AWS Console
# CloudWatch → Log Groups → /aws/elasticbeanstalk/calculator-app/
```

### CloudWatch Metrics
- CPU Utilization
- Memory Usage
- Disk Usage
- Network I/O
- Application Response Time

### Health Check
- Endpoint: `/health`
- Interval: 30 seconds
- Healthy Threshold: 2
- Unhealthy Threshold: 3

## 🎯 Auto Scaling Configuration

- **Min Instances**: 1
- **Max Instances**: 3
- **Target CPU**: 70%
- **Scale Up**: CPU > 70% for 5 minutes
- **Scale Down**: CPU < 30% for 5 minutes

## 💰 Cost Estimation

| Service | Cost |
|---------|------|
| EC2 (t3.micro, 1 instance) | ~$8/month |
| RDS (db.t3.micro) | ~$15/month |
| Data Transfer | ~$0-5/month |
| CloudWatch Logs | ~$5/month |
| **Total** | ~$28-33/month |

*Note: First 12 months may be covered by AWS Free Tier*

## 🐛 Troubleshooting

### Application won't start
```bash
# Check logs
eb logs

# Check events
eb events --follow

# SSH into instance
eb ssh
```

### Database connection error
```bash
# Verify security groups
aws ec2 describe-security-groups

# Test connection
PGPASSWORD=password psql -h endpoint -U admin -d calculator_db -c "SELECT 1"
```

### High response time
```bash
# Check instance metrics
eb health

# View database metrics
# AWS Console → RDS → Performance Insights
```

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Comprehensive step-by-step deployment guide
- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🔄 Useful Commands

```bash
# Elastic Beanstalk
eb init                    # Initialize EB project
eb create                  # Create new environment
eb deploy                  # Deploy application
eb status                  # Check status
eb health                  # View health dashboard
eb logs                    # View logs
eb setenv KEY=VALUE       # Set environment variable
eb terminate              # Delete environment

# Docker Compose
docker-compose up         # Start services
docker-compose down       # Stop services
docker-compose logs -f    # View logs
docker-compose exec app bash  # Enter app container

# AWS CLI
aws elasticbeanstalk describe-environments  # List environments
aws rds describe-db-instances               # List databases
aws cloudwatch get-metric-statistics        # Get metrics
```

## 🚀 Next Steps

1. **Implement CI/CD**
   - GitHub Actions or CodePipeline
   - Auto-deploy on push to main

2. **Add Authentication**
   - User login/registration
   - User-specific calculation history

3. **Scale Globally**
   - Multi-region deployment
   - Route 53 for geo-routing
   - CloudFront for CDN

4. **Advanced Features**
   - Calculation templates
   - Advanced math functions (sin, cos, log, etc.)
   - CSV export functionality

## 📝 License

This project is provided as-is for educational purposes.

## 💬 Support

For issues or questions, check:
1. Application logs: `eb logs --stream`
2. AWS Console for service status
3. DEPLOYMENT_GUIDE.md for detailed troubleshooting

---

**Made with ❤️ for AWS Learning**  
**Last Updated**: July 2026
