# Complete Application Deployment Process

## Overview

This document provides step-by-step instructions for deploying the Calculator Application to AWS infrastructure managed by Terraform.

**Deployment Timeline:**
1. Infrastructure with Terraform: 30-40 minutes
2. Application Deployment: 5-10 minutes
3. Total Time: ~45-50 minutes

---

## Phase 1: Infrastructure Deployment (Terraform)

### Step 1.1: Prerequisites Check

```bash
# Verify Terraform is installed
terraform version
# Expected: Terraform v1.x.x

# Verify AWS CLI is installed
aws --version
# Expected: aws-cli/2.x.x

# Verify AWS credentials are configured
aws sts get-caller-identity
# Should return your AWS account info
```

### Step 1.2: Prepare Terraform Configuration

```bash
# Create terraform directory
mkdir -p infrastructure/terraform
cd infrastructure/terraform

# Copy files from this package:
# - main.tf
# - variables.tf
# - outputs.tf
# - terraform.tfvars

# Review and edit terraform.tfvars
nano terraform.tfvars

# Change database password to something secure:
db_password = "YourSecurePassword123!@#"
```

### Step 1.3: Initialize Terraform

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt

# Expected output: "Success! The configuration is valid."
```

### Step 1.4: Plan Infrastructure

```bash
# Create execution plan
terraform plan -out=tfplan

# Review the output:
# - Should show ~45 resources to be created
# - Look for:
#   + aws_vpc.main
#   + aws_db_instance.main
#   + aws_elastic_beanstalk_app.main
#   + aws_elastic_beanstalk_environment.main
```

### Step 1.5: Deploy Infrastructure

```bash
# Apply the plan (creates AWS resources)
terraform apply tfplan

# Wait for completion (15-30 minutes)
# Watch output for:
# - VPC creation: ~2 minutes
# - RDS creation: ~10-15 minutes
# - Elastic Beanstalk: ~10-15 minutes

# Final output:
# Apply complete! Resources: X added, 0 changed, 0 destroyed.
```

### Step 1.6: Verify Infrastructure

```bash
# Get important outputs
terraform output

# Save outputs for later use
terraform output > infrastructure_info.txt

# Key outputs to note:
# - eb_cname: Your application URL
# - rds_address: Database hostname
# - eb_environment_name: EB environment name
```

### Step 1.7: Monitor Infrastructure

```bash
# Check EB environment status
aws elasticbeanstalk describe-environment-health \
  --environment-name $(terraform output -raw eb_environment_name)

# Wait for status: "Ready"
# Health: "Ok" or "Warning" (Ok is better)

# Check RDS database status
aws rds describe-db-instances \
  --db-instance-identifier calculator-app-db \
  --query 'DBInstances[0].DBInstanceStatus'

# Wait for status: "available"

# Check EC2 instances
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=calculator-app" \
  --query 'Reservations[].Instances[].InstanceId'

# Wait for instances to be in "running" state
```

---

## Phase 2: Application Deployment (Elastic Beanstalk)

### Step 2.1: Prepare Application

```bash
# Navigate to application directory
cd ../..  # Go to project root
ls
# Should see:
# - app.py
# - requirements.txt
# - templates/
# - .ebextensions/
# - Dockerfile
# - docker-compose.yml
```

### Step 2.2: Initialize Elastic Beanstalk CLI

```bash
# Install EB CLI (if not already installed)
pip install awsebcli

# Verify installation
eb --version
# Expected: EB CLI 3.x.x

# Initialize EB project
eb init -p python-3.11 calculator-app --region us-east-1

# When prompted:
# "Do you want to set up SSH?" → No
# This creates .elasticbeanstalk/config.yml
```

### Step 2.3: Connect to Existing EB Environment

```bash
# List available environments
eb list

# Should show your environment created by Terraform:
# * calculator-app-dev

# Use the environment
eb use calculator-app-dev

# Verify configuration
eb status
# Should show environment name and status
```

### Step 2.4: Deploy Application

```bash
# First deployment - upload application code
eb deploy

# Watch deployment progress
# Expected output shows:
# - Creating application version
# - Updating environment
# - Creating instances
# - Application deployed

# Estimated time: 5-10 minutes
```

### Step 2.5: Monitor Deployment

```bash
# Stream deployment logs in real-time
eb logs --stream

# Or check logs periodically
eb logs

# Look for:
# - "Successfully deployed"
# - No error messages
# - Application started successfully

# Check environment status
eb status

# Expected:
# Status: Ready
# Health: Green
```

### Step 2.6: Verify Application

```bash
# Open application in browser
eb open

# Or manually construct URL
EB_URL=$(eb status | grep "CNAME" | awk '{print $2}')
open "http://$EB_URL"

# Manual URL construction (from terraform output):
open "http://$(terraform output -raw eb_cname)"

# Test endpoint
curl http://$(terraform output -raw eb_cname)/health

# Expected response:
# {"status": "healthy", "database": "connected"}

# Test calculation API
curl -X POST http://$(terraform output -raw eb_cname)/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "10 + 5 * 2"}'

# Expected response:
# {"expression": "10 + 5 * 2", "result": 20.0, "id": 1}

# View calculation history
curl http://$(terraform output -raw eb_cname)/api/history

# View statistics
curl http://$(terraform output -raw eb_cname)/api/statistics
```

### Step 2.7: Verify Database Connection

```bash
# Get database connection details
DB_HOST=$(terraform output -raw rds_address)
echo "Database: $DB_HOST"

# Connect to database
export PGPASSWORD=$(grep db_password terraform/terraform.tfvars | awk -F'"' '{print $2}')

psql -h $DB_HOST \
  -U admin \
  -d calculator_db \
  -c "SELECT COUNT(*) FROM calculations;"

# Should return the count of calculations
# If successful: (1 row)
# If error: Check security groups and DB status

# View tables
psql -h $DB_HOST \
  -U admin \
  -d calculator_db \
  -c "\dt"

# Should show:
# calculations (PostgreSQL table)
```

---

## Phase 3: Post-Deployment Configuration

### Step 3.1: Configure Custom Domain (Optional)

```bash
# Get CNAME
EB_CNAME=$(terraform output -raw eb_cname)
echo "Point your domain to: $EB_CNAME"

# In your DNS provider (Route53, GoDaddy, etc.):
# Create CNAME record:
# Name: your-domain.com
# Value: $EB_CNAME

# Test DNS propagation
nslookup your-domain.com

# Wait until resolved
# Try again every 5 minutes until resolved
```

### Step 3.2: Enable HTTPS/SSL (Optional)

```bash
# Request free SSL certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS \
  --region us-east-1

# Get certificate ARN
CERT_ARN=$(aws acm list-certificates \
  --query 'CertificateSummaryList[0].CertificateArn' \
  --output text)

echo "Certificate ARN: $CERT_ARN"

# Update EB configuration
eb config

# In editor, find and update:
# aws:elasticbeanstalk:environment:process:default:
#   Protocol: HTTPS
#   SSLCertificateArns: $CERT_ARN

# Save and exit
# Wait for environment update (10 minutes)

# Verify HTTPS
curl https://your-domain.com/health
```

### Step 3.3: Configure Monitoring

```bash
# Enable CloudWatch monitoring
eb config

# Verify these settings:
# aws:elasticbeanstalk:cloudwatch:logs:
#   StreamLogs: true
#   RetentionInDays: 7

# Create custom alarms
aws cloudwatch put-metric-alarm \
  --alarm-name calculator-app-high-cpu \
  --alarm-description "Alert when CPU > 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:YOUR_ACCOUNT:YOUR_TOPIC
```

### Step 3.4: Configure Auto Scaling

Auto scaling is already configured by Terraform:

```bash
# Verify auto-scaling settings
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names awseb-calculator-app-dev-asg

# Current configuration:
# - Min Size: 1
# - Max Size: 3
# - CPU > 70%: Scale UP
# - CPU < 30%: Scale DOWN

# To modify:
eb config

# Update:
# aws:autoscaling:asg:
#   MinSize: 1
#   MaxSize: 5

# Save and apply
```

### Step 3.5: Set Up Automated Backups

```bash
# Backups already configured (7-day retention)
# Verify in AWS Console:
# RDS → Databases → calculator-app-db
# Backup and restore section

# View backups
aws rds describe-db-snapshots \
  --db-instance-identifier calculator-app-db

# Test restore procedure (monthly):
# 1. Create a test restore
# 2. Verify data integrity
# 3. Delete test database
```

---

## Phase 4: Continuous Deployment

### Step 4.1: Update Application Code

```bash
# Make changes to application
nano app.py

# or

nano templates/index.html

# Test locally (optional)
docker-compose up -d
# Test at http://localhost:5000
docker-compose down
```

### Step 4.2: Deploy Updates

```bash
# Simple deployment
eb deploy

# With specific version
eb deploy --version label-v1

# With message
eb deploy --message "Added new features"

# Monitor deployment
eb logs --stream

# Verify update
eb open
# Test application
```

### Step 4.3: Rollback if Needed

```bash
# List available versions
eb appversion

# If deployment fails, abort
eb abort

# Or deploy previous version
eb deploy --version previous-version-label
```

---

## Phase 5: Monitoring & Maintenance

### Step 5.1: Daily Monitoring

```bash
# Check application health
eb health

# Check logs
eb logs

# Check database size
psql -h $(terraform output -raw rds_address) \
  -U admin \
  -d calculator_db \
  -c "SELECT pg_size_pretty(pg_database_size('calculator_db'));"

# Check AWS costs
# AWS Console → Billing → Cost Explorer
```

### Step 5.2: Weekly Maintenance

```bash
# Review CloudWatch metrics
# AWS Console → CloudWatch → Dashboards

# Check error rates
# AWS Console → Elastic Beanstalk → Environment Health

# Backup verification
aws rds describe-db-snapshots \
  --db-instance-identifier calculator-app-db

# Application performance
# View response times, error rates
```

### Step 5.3: Monthly Tasks

```bash
# Review and optimize costs
# AWS Console → Cost Explorer

# Update dependencies
pip install --upgrade -r requirements.txt

# Test disaster recovery
# Restore from backup to test environment

# Review security groups
aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=calculator-app"

# Update application if needed
```

---

## Troubleshooting

### Application Won't Start

```bash
# View detailed logs
eb logs

# SSH into instance
eb ssh

# Check application
ps aux | grep gunicorn

# Check error logs
tail -f /var/log/eb-activity.log

# Check EB logs
cat /var/log/eb-engine.log
```

### Database Connection Error

```bash
# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier calculator-app-db

# Check security group
aws ec2 describe-security-groups \
  --group-ids sg-xxxxx

# Test connection
psql -h $(terraform output -raw rds_address) \
  -U admin \
  -d calculator_db \
  -c "SELECT 1;"

# Check environment variables
eb printenv | grep RDS

# SSH and test
eb ssh
psql -h $RDS_HOSTNAME -U $RDS_USERNAME -d $RDS_DB_NAME -c "SELECT 1;"
```

### High Costs

```bash
# Check running instances
aws ec2 describe-instances

# Stop unnecessary instances
aws ec2 stop-instances --instance-ids i-xxxxx

# Scale down
eb config
# Change max instances to 2

# Use Cost Explorer
# AWS Console → Billing → Cost Explorer
```

### Performance Issues

```bash
# Check CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=awseb-calculator-app-dev-asg \
  --statistics Average \
  --start-time 2024-07-05T00:00:00Z \
  --end-time 2024-07-05T23:59:59Z \
  --period 3600

# Check database slow queries
psql -h $(terraform output -raw rds_address) \
  -U admin \
  -d calculator_db \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Scale up if needed
eb scale 3  # Change to 3 instances
```

---

## Cleanup & Destruction

### Complete Cleanup

```bash
# WARNING: This destroys everything!

# Terminate EB environment
eb terminate

# Destroy all infrastructure
cd terraform
terraform destroy

# Confirm: yes

# Wait 15-20 minutes for completion

# Verify deletion
aws ec2 describe-vpcs
aws rds describe-db-instances
aws elasticbeanstalk describe-environments
```

---

## Security Checklist

Before going to production:

- [ ] Change database password to secure value
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure WAF rules
- [ ] Enable CloudTrail logging
- [ ] Enable RDS encryption
- [ ] Review security group rules
- [ ] Set up SNS notifications
- [ ] Configure backup retention (30 days min)
- [ ] Test disaster recovery
- [ ] Review IAM permissions (least privilege)

---

## Performance Checklist

- [ ] Application response time < 500ms
- [ ] Database queries optimized
- [ ] CloudWatch alarms configured
- [ ] Auto scaling tested
- [ ] Load balancer health checks working
- [ ] Cache headers configured
- [ ] CDN enabled (CloudFront optional)

---

## Quick Reference Commands

```bash
# Deployment
eb init -p python-3.11 calculator-app --region us-east-1
eb create                    # Create environment
eb deploy                    # Deploy application
eb open                      # Open in browser

# Monitoring
eb status                    # Show status
eb health                    # Show health dashboard
eb logs                      # View logs
eb logs --stream            # Stream logs
eb events --follow          # Watch events

# Configuration
eb config                    # Edit configuration
eb setenv KEY=VALUE         # Set variable
eb printenv                 # Show variables
eb scale 3                  # Scale to 3 instances

# Maintenance
eb ssh                       # Connect to instance
eb terminate                # Delete environment
eb abort                    # Abort deployment

# Infrastructure (Terraform)
terraform init              # Initialize
terraform plan              # Plan changes
terraform apply             # Apply changes
terraform destroy           # Delete resources
terraform output            # Show outputs
```

---

## Success Criteria

Your deployment is complete when:

✅ Terraform infrastructure created (all resources visible in AWS Console)  
✅ EB environment is "Ready" with "Green" health  
✅ Database is "available" and accessible  
✅ Application responds at: `http://{eb_cname}/`  
✅ Health check returns: `{"status": "healthy", "database": "connected"}`  
✅ Calculator performs calculations and saves to database  
✅ CloudWatch logs show no errors  
✅ Auto scaling is configured and working  

---

**Deployment Duration:** 45-50 minutes  
**Cost per Month:** $28-43 USD  
**Estimated Free Tier Coverage:** 12 months (80-90%)

For support, refer to:
- TERRAFORM_GUIDE.md
- DEPLOYMENT_GUIDE.md
- ARCHITECTURE.md
