# Calculator Application - AWS Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          INTERNET                               │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTPS (Port 443)
                     │
        ┌────────────▼──────────────┐
        │   Route 53 (Optional)     │
        │   Domain Routing          │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────────────┐
        │   AWS Certificate Manager         │
        │   SSL/TLS Certificates            │
        └────────────┬──────────────────────┘
                     │
        ┌────────────▼──────────────────────────────┐
        │   Elastic Load Balancer (ALB)             │
        │   - Distributes traffic                   │
        │   - Health checks                         │
        │   - Sticky sessions                       │
        │   - HTTPS termination                     │
        └────────────┬──────────────────────────────┘
                     │
        ┌────────────▼──────────────────────────────┐
        │   VPC (Virtual Private Cloud)             │
        │   CIDR: 10.0.0.0/16                       │
        │                                           │
        │  ┌──────────────┐    ┌──────────────┐    │
        │  │ Public AZ-1  │    │ Public AZ-2  │    │
        │  │ 10.0.1.0/24  │    │ 10.0.2.0/24  │    │
        │  │              │    │              │    │
        │  │ NAT Gateway  │    │ NAT Gateway  │    │
        │  └──────────────┘    └──────────────┘    │
        │         │                    │            │
        │  ┌──────▼──────┐      ┌──────▼──────┐   │
        │  │ EC2 Instance│      │ EC2 Instance│   │
        │  │ (App Server)│      │ (App Server)│   │
        │  │ t3.micro    │      │ t3.micro    │   │
        │  └──────┬──────┘      └──────┬──────┘   │
        │         │                    │           │
        │  ┌──────▼──────┐      ┌──────▼──────┐   │
        │  │ Private AZ-1│      │ Private AZ-2│   │
        │  │ 10.0.10.0/24│      │ 10.0.11.0/24│  │
        │  │              │      │              │   │
        │  └──────┬───────┘      └──────┬───────┘  │
        │         │                    │            │
        │  ┌──────▼────────────────────▼──────┐   │
        │  │   RDS PostgreSQL Database         │   │
        │  │   - Multi-AZ deployment           │   │
        │  │   - Automated backups             │   │
        │  │   - Encrypted at rest             │   │
        │  │   - db.t3.micro instance          │   │
        │  └───────────────────────────────────┘   │
        │                                           │
        └───────────────────────────────────────────┘
                     │
        ┌────────────▼──────────────────────┐
        │  CloudWatch                       │
        │  - Logs                           │
        │  - Metrics                        │
        │  - Alarms                         │
        │  - Dashboards                     │
        └──────────────────────────────────┘
                     │
        ┌────────────▼──────────────────────┐
        │  CloudWatch Events                │
        │  - Auto Scaling Triggers          │
        │  - Health Check Notifications     │
        │  - SNS Email Alerts               │
        └──────────────────────────────────┘
```

---

## Component Descriptions

### 1. Internet & Routing Layer

#### AWS Certificate Manager
- **Purpose**: SSL/TLS certificates for HTTPS
- **Features**:
  - Free SSL certificates
  - Auto-renewal
  - No additional charges
- **Configuration**: Applied to ALB for HTTPS termination

#### Route 53 (Optional)
- **Purpose**: Domain name management
- **Features**:
  - DNS routing
  - Health checks
  - Geo-routing
- **Configuration**: Point domain to ALB CNAME

---

### 2. Load Balancing Layer

#### Application Load Balancer (ALB)
- **Purpose**: Distribute incoming traffic to EC2 instances
- **Location**: Public subnets across 2 AZs
- **Features**:
  - Layer 7 (Application layer) routing
  - Path-based routing (if needed)
  - Host-based routing
  - Health checks every 30 seconds
  - Sticky sessions (optional)
  - Cross-zone load balancing
- **Security**:
  - Inbound: 80 (HTTP), 443 (HTTPS)
  - Outbound: To EC2 instances on port 5000
- **Monitoring**: CloudWatch metrics for request count, latency, errors

---

### 3. Application Layer (Elastic Beanstalk)

#### EC2 Instances
- **Number**: 1-3 instances (auto-scaling)
- **Type**: t3.micro (eligible for free tier)
- **Location**: Private subnets across 2 AZs
- **Operating System**: Amazon Linux 2
- **Application**: Python Flask + Gunicorn
- **Port**: 5000 (internal), exposed via ALB

#### Instance Configuration
```
├── Python 3.11
├── Flask Web Framework
├── Gunicorn Application Server
│   ├── 3 worker processes
│   ├── 2 threads per worker
│   └── 60-second timeout
├── PostgreSQL Client (psycopg2)
└── CloudWatch Agent
```

#### Auto Scaling
- **Min Size**: 1 instance
- **Max Size**: 3 instances
- **Metric**: CPU Utilization
- **Scale Up**: CPU > 70% for 5 minutes
- **Scale Down**: CPU < 30% for 5 minutes
- **Cooldown**: 5 minutes between scaling actions

---

### 4. Network Layer (VPC)

#### VPC Configuration
- **CIDR Block**: 10.0.0.0/16
- **Subnets**: 4 total (2 public, 2 private)
- **AZs**: us-east-1a, us-east-1b
- **Internet Gateway**: Attached to VPC

#### Public Subnets (AZ-1, AZ-2)
- **CIDR**: 10.0.1.0/24, 10.0.2.0/24
- **Purpose**: NAT gateways, ALB
- **Route Table**:
  - 0.0.0.0/0 → Internet Gateway
  - 10.0.0.0/16 → Local

#### Private Subnets (AZ-1, AZ-2)
- **CIDR**: 10.0.10.0/24, 10.0.11.0/24
- **Purpose**: EC2 instances, RDS database
- **Route Table**:
  - 0.0.0.0/0 → NAT Gateway (for internet access)
  - 10.0.0.0/16 → Local

#### Security Groups

##### ALB Security Group
```
Inbound Rules:
  - HTTP (80) from 0.0.0.0/0
  - HTTPS (443) from 0.0.0.0/0
Outbound Rules:
  - All traffic to EC2 security group
```

##### EC2 Instance Security Group
```
Inbound Rules:
  - TCP 5000 from ALB security group
  - TCP 443 from 0.0.0.0/0 (if direct access needed)
Outbound Rules:
  - All traffic (for API calls, updates)
  - TCP 5432 to RDS security group
```

##### RDS Security Group
```
Inbound Rules:
  - PostgreSQL (5432) from EC2 security group
Outbound Rules:
  - None (database doesn't initiate outbound)
```

---

### 5. Database Layer (RDS)

#### RDS PostgreSQL
- **Engine**: PostgreSQL 15
- **Instance Class**: db.t3.micro
- **Storage**: 20 GB (auto-scaling enabled)
- **Backup Retention**: 7 days
- **Multi-AZ**: Yes (automated failover)
- **Encryption**: At rest (KMS)

#### Database Details
- **Name**: calculator_db
- **Username**: admin
- **Password**: User-provided (stored in AWS Secrets Manager)
- **Port**: 5432 (default)
- **Maintenance Window**: Sunday 03:00-04:00 UTC

#### Backup Strategy
- **Automated Backups**: Daily
- **Backup Window**: 03:00-04:00 UTC
- **Retention Period**: 7 days
- **Multi-AZ Backups**: Yes
- **Restore Option**: Point-in-time recovery

#### Database Schema
```sql
CREATE TABLE calculations (
  id SERIAL PRIMARY KEY,
  expression VARCHAR(255) NOT NULL,
  result FLOAT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_ip VARCHAR(45),
  
  -- Indexes for performance
  INDEX idx_timestamp (timestamp DESC),
  INDEX idx_user_ip (user_ip)
);
```

---

### 6. Monitoring & Logging

#### CloudWatch
- **Location**: All AWS regions
- **Features**:
  - Centralized logging
  - Metrics collection
  - Alarm management
  - Dashboard visualization

#### Log Groups
```
/aws/elasticbeanstalk/calculator-app/
├── var/log/eb-activity.log          # EB deployment logs
├── var/log/eb-engine.log            # EB engine logs
├── var/log/eb-publish.log           # EB publish logs
└── var/log/httpd/error_log          # Application errors
```

#### Metrics Collected
- **EC2 Metrics**:
  - CPU Utilization
  - Memory Usage
  - Disk I/O
  - Network I/O
  
- **ALB Metrics**:
  - Active Connection Count
  - Request Count
  - Response Time
  - HTTP 4xx/5xx Errors
  
- **RDS Metrics**:
  - CPU Utilization
  - Database Connections
  - Read/Write Latency
  - Storage Space Used

#### Alarms
- **High CPU**: CPU > 70% for 5 minutes
- **Database Connection**: Active > 80
- **Disk Space**: Usage > 80%
- **Error Rate**: 5xx errors > 5%
- **Response Time**: > 1000ms average

---

## Data Flow

### Incoming Request Flow
```
1. User Request
   ↓
2. Route 53 (DNS Resolution)
   ↓
3. ALB (80/443)
   ↓
4. Health Check (if healthy)
   ↓
5. EC2 Instance (Flask App on port 5000)
   ↓
6. Request Processing
   - Validate input
   - Perform calculation
   - Save to PostgreSQL
   ↓
7. Response
   ↓
8. ALB Sends Response
   ↓
9. Client Receives Response
```

### Database Interaction Flow
```
1. Application receives calculation request
   ↓
2. Flask validates expression
   ↓
3. Evaluates mathematical expression
   ↓
4. Creates Calculation object
   ↓
5. SQLAlchemy ORM
   ↓
6. PostgreSQL query execution
   ↓
7. Data persisted to disk
   ↓
8. Multi-AZ replication (if enabled)
   ↓
9. Response returned to application
```

---

## Scaling Behavior

### Horizontal Scaling (Add Instances)
```
Normal State: 1 instance
     ↓
CPU Utilization > 70%
     ↓
[Wait 5 minutes]
     ↓
Auto Scaling Group triggers
     ↓
Launch new EC2 instance
     ↓
Register with Target Group
     ↓
Pass health checks
     ↓
Add to Load Balancer (100+ instances max: 3)
```

### Vertical Scaling (Upgrade Instance)
- Change instance type (manual, no downtime with ALB)
- Increase EBS storage
- Upgrade RDS instance class

---

## Disaster Recovery

### RDS Multi-AZ Failover
```
Primary DB (AZ-1)
    ↓
Synchronous replication
    ↓
Standby DB (AZ-2)
    ↓
[If primary fails]
    ↓
Automatic failover (< 2 minutes)
    ↓
Standby becomes primary
    ↓
Application reconnects
```

### Application Instance Failure
```
Instance 1 fails
    ↓
ALB health check fails
    ↓
Remove from target group
    ↓
Auto Scaling launches replacement
    ↓
New instance registers with ALB
    ↓
Traffic resumes
```

### Regional Failure (Optional)
- Can deploy to multiple regions
- Use Route 53 for failover
- Requires RDS read replicas in other regions

---

## Security Architecture

### Network Security
- **VPC Isolation**: Private subnets for compute
- **Security Groups**: Least privilege access
- **NACLs**: Optional additional layer
- **VPC Flow Logs**: Monitor traffic

### Data Security
- **Encryption in Transit**: HTTPS/TLS
- **Encryption at Rest**: RDS KMS encryption
- **Database Access**: From app servers only
- **Backups**: Encrypted, retained 7 days

### Application Security
- **IAM Roles**: Specific permissions only
- **Secrets Management**: Passwords in AWS Secrets Manager
- **CloudTrail**: Audit all API calls
- **WAF**: Optional Web Application Firewall

---

## Cost Analysis

### Monthly Cost Breakdown
| Component | Instance Type | Quantity | Unit Cost | Total |
|-----------|---------------|----------|-----------|-------|
| EC2 | t3.micro | 1 (avg) | $8.51 | $8.51 |
| RDS | db.t3.micro | 1 | $15.07 | $15.07 |
| ALB | ALB | 1 | $22.50 | $22.50 |
| Data Transfer | Out | 1 GB | $0.09 | $0.09 |
| CloudWatch | Logs | 5 GB | $0.50 | $2.50 |
| S3 (optional) | Storage | - | - | - |
| **Total** | | | | **$48.67** |

**Note**: AWS Free Tier covers first 12 months

---

## Performance Characteristics

### Application Performance
- **Response Time**: < 500ms (database + application)
- **Throughput**: 100-1000 requests/second (t3.micro)
- **Concurrent Users**: 100-500
- **Database Latency**: 5-10ms

### Scaling Thresholds
- **Single Instance**: Up to 200 requests/second
- **Two Instances**: Up to 400 requests/second
- **Three Instances**: Up to 600 requests/second

---

## Deployment Options

### Option 1: Elastic Beanstalk (Recommended)
- **Ease**: ★★★★★
- **Control**: ★★★☆☆
- **Cost**: ★★★★☆
- **Time**: 15 minutes

### Option 2: EC2 with Manual Setup
- **Ease**: ★★☆☆☆
- **Control**: ★★★★★
- **Cost**: ★★★☆☆
- **Time**: 2 hours

### Option 3: ECS Fargate (Container)
- **Ease**: ★★★★☆
- **Control**: ★★★★☆
- **Cost**: ★★★☆☆
- **Time**: 30 minutes

---

## Future Enhancements

### Architecture Improvements
1. **CloudFront CDN**
   - Cache static assets
   - Global distribution

2. **ElastiCache Redis**
   - Cache calculation history
   - Session storage

3. **S3 for Static Assets**
   - Offload images/CSS/JS
   - Reduce ALB load

4. **SNS Notifications**
   - Email alerts
   - SMS notifications

5. **Lambda Functions**
   - Scheduled backups
   - Data cleanup

6. **DynamoDB**
   - Alternative for NoSQL workloads
   - Global tables for multi-region

---

## Monitoring Dashboard

### Key Metrics to Watch
1. **Availability**: Target = 99.9% uptime
2. **Latency**: Target = < 500ms p95
3. **Error Rate**: Target = < 0.1%
4. **CPU Usage**: Target = 40-60%
5. **Database Connections**: Target = < 50
6. **Disk Usage**: Target = < 80%

### Alert Thresholds
- CPU > 70%: Add instance
- CPU < 20%: Remove instance
- Error rate > 1%: Page on-call
- Database connections > 80: Investigate
- Disk usage > 90%: Urgent scaling

---

**Architecture Version**: 1.0  
**Last Updated**: July 2026  
**Suitable For**: Development, Testing, Small Production (< 1M calculations/month)

For production at scale, consider:
- Multi-region deployment
- Database read replicas
- Advanced caching strategies
- Dedicated security analysis
