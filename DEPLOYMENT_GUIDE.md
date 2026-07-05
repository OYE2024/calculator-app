# Online Calculator Application - AWS Elastic Beanstalk Deployment Guide

## Project Overview

This is a simple yet powerful online calculator web application with the following features:

- **Frontend**: Clean, responsive HTML5 interface with real-time calculation
- **Backend**: Python Flask REST API
- **Database**: PostgreSQL for storing calculation history
- **Infrastructure**: AWS Elastic Beanstalk with RDS
- **Deployment**: Containerized with Docker

### Application Features

1. **Calculator Functionality**
   - Perform mathematical calculations (addition, subtraction, multiplication, division)
   - Support for parentheses and complex expressions
   - Real-time result display

2. **History & Storage**
   - All calculations saved to PostgreSQL database
   - View calculation history with timestamps
   - Delete individual calculations

3. **Statistics**
   - Total number of calculations
   - Average result
   - Minimum and maximum results

4. **Health Monitoring**
   - Health check endpoint for load balancer
   - Database connectivity monitoring
   - Application logging

---

## Project Structure

```
calculator-app/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Local development setup
├── .ebignore                       # Files to ignore in EB deployment
├── .env.example                    # Environment variables template
├── templates/
│   └── index.html                  # Web interface
├── static/                         # Static assets (CSS, JS)
└── .ebextensions/
    ├── 01_python.config            # Python & app configuration
    ├── 02_rds.config               # Database configuration
    └── 03_healthcheck.config       # Health check & scaling
```

---

## Prerequisites

Before you start, ensure you have:

1. **AWS Account**
   - Active AWS account with billing enabled
   - IAM user with appropriate permissions
   - AWS CLI configured locally

2. **Local Development Tools**
   ```bash
   # Install AWS CLI
   pip install awscli
   
   # Install EB CLI
   pip install awsebcli
   
   # Install Docker
   # Download from https://www.docker.com/products/docker-desktop
   ```

3. **Git**
   ```bash
   # For version control and deployment
   git --version
   ```

---

## Part 1: Local Development Setup

### Step 1: Clone or Create Project

```bash
mkdir calculator-app
cd calculator-app
git init
```

### Step 2: Copy Project Files

Copy all files from the provided package:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `.ebignore`
- `.env.example`
- `templates/index.html`

### Step 3: Set Up Local Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run Locally with Docker Compose

```bash
# Build and run containers
docker-compose up -d

# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f app
```

Access the application: **http://localhost:5000**

### Step 5: Test Local Application

```bash
# Test API
curl http://localhost:5000/health

# Test calculation
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "10 + 5 * 2"}'

# View history
curl http://localhost:5000/api/history
```

### Step 6: Stop Local Environment

```bash
docker-compose down
```

---

## Part 2: AWS Setup

### Step 1: Create AWS IAM User

1. Go to AWS Console → IAM → Users
2. Create new user `calculator-deployer`
3. Attach policies:
   - `ElasticBeanstalkFullAccess`
   - `RDSFullAccess`
   - `EC2FullAccess`
   - `IAMFullAccess`
   - `CloudWatchLogsFullAccess`

### Step 2: Configure AWS CLI

```bash
# Configure credentials
aws configure

# Enter:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json
```

### Step 3: Create VPC and Subnets (Optional)

For better security, create a custom VPC:

```bash
# Or use AWS Console → VPC → Create VPC
# Create public and private subnets
# Attach Internet Gateway
# Configure NAT Gateway for private subnet
```

### Step 4: Create RDS Security Group

```bash
# In AWS Console → VPC → Security Groups
# Create security group for RDS
# Inbound rule: PostgreSQL (5432) from EC2 security group
```

---

## Part 3: Elastic Beanstalk Deployment

### Step 1: Initialize Elastic Beanstalk

```bash
# In your project directory
eb init -p python-3.11 calculator-app --region us-east-1

# Follow prompts to:
# - Choose region
# - Create new application
# - Use code commit (optional)
```

### Step 2: Create Environment

```bash
# Create development environment
eb create calculator-dev \
  --instance-type t3.micro \
  --envvars RDS_HOSTNAME=your-rds-endpoint,RDS_USERNAME=admin,RDS_PASSWORD=your-password,RDS_DB_NAME=calculator_db

# Wait for environment to be created (5-10 minutes)
eb status
```

### Step 3: Check Environment Status

```bash
# View environment details
eb status

# View environment health
eb health

# View recent logs
eb logs

# Open application in browser
eb open
```

### Step 4: Configure Environment Variables

```bash
# Using EB CLI
eb setenv RDS_HOSTNAME=your-rds-endpoint \
          RDS_USERNAME=admin \
          RDS_PASSWORD=your-secure-password \
          RDS_DB_NAME=calculator_db \
          RDS_PORT=5432

# Or use AWS Console → Elastic Beanstalk → Environment → Configuration
```

### Step 5: Deploy Application Updates

```bash
# Make changes to your code

# Deploy to Elastic Beanstalk
eb deploy

# Check deployment status
eb status

# View real-time logs
eb logs --stream
```

---

## Part 4: RDS Database Setup

### Option A: Using Elastic Beanstalk RDS

The `.ebextensions/02_rds.config` automatically creates RDS instance.

### Option B: Creating Separate RDS Instance

```bash
# Create RDS instance via AWS CLI
aws rds create-db-instance \
  --db-instance-identifier calculator-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password your-secure-password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxx \
  --db-name calculator_db \
  --backup-retention-period 7 \
  --publicly-accessible false

# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier calculator-db \
  --query 'DBInstances[0].Endpoint.Address'
```

### Step 2: Initialize Database

```bash
# Connect to RDS
PGPASSWORD=your-password psql -h your-rds-endpoint -U admin -d calculator_db

# Application will auto-create tables on first run
# Or manually: python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## Part 5: Load Balancer & Auto Scaling

### Configure Load Balancer

```bash
# Using EB CLI
eb config

# In YAML editor, find and modify:
aws:elasticbeanstalk:environment:process:default:
  HealthCheckPath: /health
  HealthCheckInterval: 30
  HealthyThreshold: 2
  UnhealthyThreshold: 3
```

### Configure Auto Scaling

```bash
# Using EB CLI
eb config

# Add auto-scaling rules:
aws:autoscaling:asg:
  MinSize: 1
  MaxSize: 3

aws:autoscaling:trigger:
  MeasureName: CPUUtilization
  Statistic: Average
  Unit: Percent
  UpperThreshold: 70
  LowerThreshold: 30
```

### Enable CloudWatch Monitoring

```bash
# Using EB CLI
eb config

# Enable:
aws:elasticbeanstalk:cloudwatch:logs:
  StreamLogs: true
  RetentionInDays: 7
```

---

## Part 6: HTTPS/SSL Configuration

### Option A: Using AWS Certificate Manager

```bash
# Request free SSL certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS

# Validate domain ownership via DNS

# Apply certificate to load balancer
# AWS Console → EC2 → Load Balancers → Listeners → Edit → HTTPS (443)
```

### Option B: Using Let's Encrypt

```bash
# Create .ebextensions/04_https.config
option_settings:
  aws:elasticbeanstalk:environment:process:default:
    InstanceProtocol: HTTP
    Protocol: HTTPS
    SSLCertificateArns: arn:aws:acm:region:account:certificate/id
```

### Redirect HTTP to HTTPS

```python
# In app.py, add:
@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```

---

## Part 7: Monitoring & Logging

### CloudWatch Logs

```bash
# View application logs
eb logs

# Tail logs in real-time
eb logs --stream

# View in AWS Console
# CloudWatch → Log Groups → /aws/elasticbeanstalk/calculator-app/
```

### CloudWatch Alarms

```bash
# Create alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name calculator-high-cpu \
  --alarm-description "Alert when CPU > 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:region:account:topic-name
```

### Application Metrics

```bash
# Check health endpoint
curl https://your-app.elasticbeanstalk.com/health

# View statistics
curl https://your-app.elasticbeanstalk.com/api/statistics
```

---

## Part 8: Cost Optimization

### Estimated Monthly Costs

| Service | Instance Type | Monthly Cost |
|---------|---------------|-------------|
| EC2 | t3.micro (1) | $8 |
| RDS | db.t3.micro | $15 |
| Data Transfer | Minimal | $0-5 |
| CloudWatch Logs | 1 week retention | $5 |
| **Total** | | **$28-33** |

### Cost Optimization Tips

1. **Right-size instances**
   ```bash
   # Monitor actual usage
   eb health --refresh
   
   # Scale down if needed
   eb scale 1  # Single instance
   ```

2. **Use AWS Free Tier**
   - 12 months free t2.micro (or t3.micro with credits)
   - 750 hours per month

3. **Set up budgets**
   ```bash
   # AWS Console → Billing → Budgets
   # Create monthly budget alert at $50
   ```

4. **Reserved Instances**
   - Purchase 1-year RI for 30% savings
   - Use Spot instances for non-critical apps

---

## Part 9: Troubleshooting

### Application won't start

```bash
# Check logs
eb logs

# Check events
eb events --follow

# SSH into instance (if needed)
eb ssh
```

### Database connection errors

```bash
# Verify RDS security group
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Test connection
PGPASSWORD=password psql -h endpoint -U admin -d calculator_db -c "SELECT 1"
```

### High latency

```bash
# Check instance metrics
eb health

# Review database slow queries
aws rds describe-db-log-files --db-instance-identifier calculator-db

# Scale up if needed
eb scale 2  # Add more instances
```

### Deployment failures

```bash
# Roll back to previous version
eb abort

# Deploy specific version
eb deploy --version label-name
```

---

## Part 10: Cleanup & Termination

### Temporary Stop (Keep for later)

```bash
# Pause environment
eb pause
```

### Resume Environment

```bash
# Resume from paused state
eb resume
```

### Permanent Deletion

```bash
# Terminate environment
eb terminate

# This will delete:
# - EC2 instances
# - Load balancer
# - Attached RDS (if configured)
# - Auto Scaling group
```

---

## Important Security Practices

✅ **DO:**
- Store passwords in AWS Secrets Manager
- Enable RDS encryption at rest
- Use VPC for network isolation
- Enable CloudTrail for audit logging
- Use SSL/TLS for all communications
- Implement WAF rules on load balancer

❌ **DON'T:**
- Hard-code credentials in code
- Use simple passwords
- Allow public access to RDS
- Disable CloudWatch logging
- Use self-signed certificates in production
- Share AWS credentials

---

## Useful Commands Reference

```bash
# Environment management
eb init                    # Initialize EB project
eb create                  # Create new environment
eb deploy                  # Deploy application
eb terminate              # Delete environment
eb status                 # Check environment status
eb health                 # View health dashboard
eb logs                   # View logs

# Configuration
eb config                 # Edit environment configuration
eb setenv KEY=VALUE      # Set environment variable
eb appversion            # Manage application versions

# Monitoring
eb events                # View environment events
eb scale NUMBER          # Change number of instances
eb ssh                   # SSH into EC2 instance

# Troubleshooting
eb abort                 # Abort current deployment
eb printenv              # Print environment variables
eb platform              # Manage platform versions
```

---

## Additional Resources

- **AWS Elastic Beanstalk Documentation**: https://docs.aws.amazon.com/elasticbeanstalk/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **AWS RDS Documentation**: https://docs.aws.amazon.com/rds/
- **Gunicorn Documentation**: https://gunicorn.org/

---

## Support & Debugging

### Check Application Logs

```bash
# Real-time logs
eb logs --stream

# Save logs locally
eb logs > app-logs.txt

# Check specific log group
aws logs tail /aws/elasticbeanstalk/calculator-app/var/log/eb-activity.log --follow
```

### Monitor Database

```bash
# Connect to database
PGPASSWORD=password psql -h endpoint -U admin -d calculator_db

# View tables
\dt

# View records
SELECT * FROM calculations ORDER BY timestamp DESC LIMIT 10;

# Check database size
SELECT pg_size_pretty(pg_database_size('calculator_db'));
```

### Performance Testing

```bash
# Simple load test
for i in {1..100}; do
  curl -X POST https://your-app.elasticbeanstalk.com/api/calculate \
    -H "Content-Type: application/json" \
    -d "{\"expression\": \"$i + 1\"}"
done
```

---

## Next Steps

1. **Implement CI/CD Pipeline**
   - Use GitHub Actions or CodePipeline
   - Auto-deploy on commits

2. **Add Authentication**
   - Implement user login
   - Store user-specific calculation history

3. **Scale to Multi-Region**
   - Replicate to multiple AWS regions
   - Use Route 53 for geo-routing

4. **Implement Advanced Features**
   - Calculation templates
   - Advanced mathematical functions
   - Data export functionality

---

**Version**: 1.0  
**Last Updated**: July 2026  
**Author**: AWS Solutions Team
