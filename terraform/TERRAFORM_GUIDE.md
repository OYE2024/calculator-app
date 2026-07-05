# Terraform Infrastructure as Code - Complete Guide

## Overview

This guide walks you through using Terraform to automatically provision all AWS infrastructure for the Calculator Application.

**What Terraform Creates:**
- VPC with 2 public and 2 private subnets (2 AZs)
- Internet Gateway and NAT Gateways
- Security Groups for ALB, EC2, and RDS
- RDS PostgreSQL database
- Elastic Beanstalk application and environment
- Auto Scaling configuration
- CloudWatch logging

---

## Prerequisites

### 1. Install Required Tools

```bash
# Terraform (macOS - using Homebrew)
brew install terraform

# Terraform (Windows - using Chocolatey)
choco install terraform

# Terraform (Linux - direct download)
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
```

### 2. AWS CLI

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json
```

### 3. AWS Account Setup

- Create AWS account and enable billing
- Create IAM user with `Administrator` or equivalent permissions
- Generate AWS Access Keys (ID + Secret)

---

## Directory Structure

```
terraform/
├── main.tf              # Main infrastructure definition
├── variables.tf         # Variable definitions
├── outputs.tf           # Output values
├── terraform.tfvars     # Variable values (DO NOT COMMIT!)
├── .gitignore          # Ignore sensitive files
└── README.md           # This file
```

---

## Step 1: Prepare Configuration

### Copy Terraform Files

Create a `terraform` directory in your project:

```bash
mkdir terraform
cd terraform

# Copy files:
# - main.tf
# - variables.tf
# - outputs.tf
# - terraform.tfvars
```

### Edit terraform.tfvars

**IMPORTANT: Change the database password!**

```hcl
db_password = "ChangeMe123!Pass"  # Change this to a strong password
```

**Other important settings:**

```hcl
aws_region   = "us-east-1"        # Change if needed
environment  = "dev"               # dev, staging, or prod
project_name = "calculator-app"    # Your project name

# For production:
db_multi_az     = true             # High availability
eb_instance_type = "t3.small"      # Larger instance
eb_max_instances = 5               # More instances
```

### Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Terraform files
.terraform/
*.tfstate
*.tfstate.*
.terraform.lock.hcl

# IDE
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Sensitive
terraform.tfvars
*.backup
EOF
```

---

## Step 2: Initialize Terraform

### Initialize Terraform Project

```bash
# In terraform directory
terraform init

# Output should show:
# Terraform has been successfully configured!
# You may now begin working with Terraform.
```

This downloads the AWS provider and sets up local state.

### Verify Configuration

```bash
# Validate configuration syntax
terraform validate

# Format code (optional)
terraform fmt

# Output:
# Success! The configuration is valid.
```

---

## Step 3: Plan Infrastructure

### Create Execution Plan

```bash
# Preview all changes
terraform plan -out=tfplan

# Save plan to file (recommended)
# terraform plan -out=tfplan
```

**Review the plan output:**
- `+` indicates resources to be created
- Check resource counts (should be ~40+ resources)
- Verify database password is masked

### Example Output

```
Terraform will perform the following actions:

  # aws_vpc.main will be created
  + resource "aws_vpc" "main" {
      + availability_zone = "us-east-1a"
      + cidr_block        = "10.0.0.0/16"
      ...
    }

Plan: 45 to add, 0 to change, 0 to destroy.
```

---

## Step 4: Apply Infrastructure

### Deploy to AWS

```bash
# Apply the plan (creates actual resources)
terraform apply tfplan

# Or without saved plan (will ask for confirmation)
terraform apply

# When prompted, type: yes

# Wait 15-30 minutes for full deployment
# - VPC: ~2 minutes
# - RDS: ~10-15 minutes
# - Elastic Beanstalk: ~10-15 minutes
```

### Monitor Progress

```bash
# Watch EC2 instances
aws ec2 describe-instances --region us-east-1

# Check RDS status
aws rds describe-db-instances --db-instance-identifier calculator-app-db

# Check EB status
aws elasticbeanstalk describe-environment-health \
  --environment-name calculator-app-dev
```

---

## Step 5: Retrieve Outputs

### Get Important Information

```bash
# Display all outputs
terraform output

# Get specific output
terraform output eb_cname
terraform output rds_address

# Example output:
# eb_cname = "calculator-app-dev-xxxxxx.us-east-1.elasticbeanstalk.com"
# rds_address = "calculator-app-db.xxxxx.us-east-1.rds.amazonaws.com"
```

### Environment Variables

Terraform automatically sets RDS credentials as EB environment variables:
- `RDS_HOSTNAME` - Database host
- `RDS_PORT` - Database port (5432)
- `RDS_DB_NAME` - Database name
- `RDS_USERNAME` - Database user (admin)
- `RDS_PASSWORD` - Your password

---

## Step 6: Deploy Application

### Initialize Elastic Beanstalk

```bash
# In application directory (where app.py is)
eb init -p python-3.11 calculator-app --region us-east-1

# Choose to use existing EB application: Yes
# Select existing application: calculator-app
# Select existing environment: calculator-app-dev
```

### Deploy Application Code

```bash
# Deploy application
eb deploy

# Watch deployment
eb logs --stream

# Check status
eb status
```

### Verify Deployment

```bash
# Open application in browser
eb open

# Test health endpoint
curl http://$(terraform output -raw eb_cname)/health
# Should return: {"status": "healthy", "database": "connected"}

# Test calculation
curl -X POST http://$(terraform output -raw eb_cname)/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "10 + 5"}'
```

---

## Step 7: Configure Domain (Optional)

### Point Domain to Application

```bash
# Get CNAME
terraform output eb_cname

# In DNS provider (GoDaddy, Route53, etc.):
# Create CNAME record:
# Name: your-domain.com
# Value: <cname-from-above>

# Verify DNS propagation
nslookup your-domain.com
```

### Enable HTTPS

```bash
# Request SSL certificate (free)
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS

# Get certificate ARN
aws acm list-certificates

# Update EB configuration
eb config

# Add HTTPS listener:
aws:elasticbeanstalk:environment:process:default:
  Protocol: HTTPS
  SSLCertificateArns: arn:aws:acm:...
```

---

## Managing Infrastructure

### View Current State

```bash
# Show all managed resources
terraform show

# Show state file
terraform state list

# Show specific resource
terraform state show aws_db_instance.main
```

### Update Configuration

### Update Variables

```bash
# Edit terraform.tfvars
nano terraform.tfvars

# Change settings (e.g., increase max instances)
eb_max_instances = 5

# Apply changes
terraform plan
terraform apply
```

### Scale Application

```bash
# Auto Scaling is already configured
# Current triggers:
# - Scale UP: CPU > 70% for 5 minutes
# - Scale DOWN: CPU < 30% for 5 minutes
# - Min instances: 1
# - Max instances: 3

# To modify scaling, edit terraform.tfvars:
eb_min_instances = 2
eb_max_instances = 10

# Apply changes
terraform apply
```

### Update RDS

```bash
# Change instance type
db_instance_class = "db.t3.small"

# Create snapshot before upgrade
db_create_snapshot_on_delete = true

# Enable Multi-AZ
db_multi_az = true

# Apply changes
terraform apply
```

---

## Monitoring & Maintenance

### CloudWatch Logs

```bash
# View EB logs
eb logs

# Stream logs in real-time
eb logs --stream

# Access CloudWatch
# AWS Console → CloudWatch → Log Groups → /aws/elasticbeanstalk/calculator-app/
```

### Health Checks

```bash
# EB environment health
aws elasticbeanstalk describe-environment-health \
  --environment-name calculator-app-dev

# RDS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=calculator-app-db \
  --statistics Average \
  --start-time 2024-07-05T00:00:00Z \
  --end-time 2024-07-05T23:59:59Z \
  --period 3600
```

### Database Maintenance

```bash
# Connect to database (after deployment)
export DB_HOST=$(terraform output -raw rds_address)
psql -h $DB_HOST -U admin -d calculator_db

# View tables
\dt

# View records
SELECT * FROM calculations LIMIT 10;

# Check database size
SELECT pg_size_pretty(pg_database_size('calculator_db'));
```

---

## Troubleshooting

### Terraform Won't Apply

```bash
# Check syntax errors
terraform validate

# Check for locking issues
rm .terraform/terraform.tfstate.lock.hcl

# Try again with verbose output
terraform apply -var-file="terraform.tfvars" -input=false

# Check AWS credentials
aws sts get-caller-identity
```

### EB Environment Stuck

```bash
# Terminate stuck environment
aws elasticbeanstalk terminate-environment \
  --environment-name calculator-app-dev

# Redeploy
terraform apply
```

### RDS Won't Connect

```bash
# Check security group
aws ec2 describe-security-groups \
  --group-ids sg-xxxxxxxx

# Verify DB is running
aws rds describe-db-instances \
  --db-instance-identifier calculator-app-db

# Check status should be "available"
```

### Out of Resources

```bash
# Destroy all resources
terraform destroy

# Confirm: yes

# All AWS resources will be deleted
```

---

## Cost Optimization

### Monitor Costs

```bash
# Enable AWS Cost Explorer
# AWS Console → Billing → Cost Explorer

# Set budget alerts
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://budget.json
```

### Reduce Costs

```bash
# Option 1: Stop environment (not destroy)
eb halt

# Resume later
eb resume

# Option 2: Reduce instances
eb_min_instances = 1
eb_max_instances = 2

# Option 3: Smaller instance types
eb_instance_type = "t3.nano"    # Free tier
db_instance_class = "db.t3.micro"

terraform apply
```

---

## Destruction (Cleanup)

### Delete All Infrastructure

```bash
# Warn! This deletes everything

# Plan destruction
terraform plan -destroy

# Destroy resources
terraform destroy

# Confirm: yes

# Wait for completion (10-15 minutes)
```

### Verify Deletion

```bash
# Check AWS Console
# - VPC deleted
# - RDS deleted
# - EB environment deleted
# - Security groups deleted

# Check via CLI
aws ec2 describe-vpcs --region us-east-1
aws rds describe-db-instances --region us-east-1
```

---

## Best Practices

### Security

✅ **DO:**
- Store `terraform.tfvars` in `.gitignore`
- Use strong database passwords
- Enable RDS encryption
- Use AWS Secrets Manager for credentials
- Enable MFA on AWS account
- Use IAM roles with minimal permissions

❌ **DON'T:**
- Commit `terraform.tfvars` to Git
- Use simple passwords
- Disable security groups
- Share AWS credentials
- Use root AWS account
- Expose sensitive outputs

### Version Control

```bash
# Good .gitignore
.terraform/
*.tfstate*
terraform.tfvars
.DS_Store
*.swp

# Track these files
main.tf
variables.tf
outputs.tf
.gitignore
README.md
```

### State Management

```bash
# Always back up state
aws s3 cp terraform.tfstate s3://my-backup-bucket/

# Use remote state for team environments
# Add to main.tf:
# terraform {
#   backend "s3" {
#     bucket = "terraform-state"
#     key    = "calculator-app/terraform.tfstate"
#     region = "us-east-1"
#   }
# }
```

---

## Common Commands Reference

```bash
# Initialize
terraform init

# Validate
terraform validate

# Format
terraform fmt

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Show outputs
terraform output

# Show state
terraform show

# List resources
terraform state list

# Show resource
terraform state show aws_db_instance.main

# Refresh state
terraform refresh

# Destroy
terraform destroy

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0
```

---

## Support & Debugging

### Enable Debug Logging

```bash
# Verbose output
TF_LOG=DEBUG terraform apply

# Save logs
TF_LOG=DEBUG terraform apply > terraform.log 2>&1

# Different levels: TRACE, DEBUG, INFO, WARN, ERROR
```

### Check AWS Resources

```bash
# List all EC2 instances
aws ec2 describe-instances --region us-east-1

# List all RDS instances
aws rds describe-db-instances

# List all EB apps
aws elasticbeanstalk describe-applications

# List all EB environments
aws elasticbeanstalk describe-environments
```

---

## Next Steps

1. ✅ Install Terraform
2. ✅ Configure AWS credentials
3. ✅ Edit `terraform.tfvars` with your values
4. ✅ Run `terraform init`
5. ✅ Run `terraform plan`
6. ✅ Run `terraform apply`
7. ✅ Deploy application with `eb deploy`
8. ✅ Monitor and maintain

---

## Resources

- **Terraform Docs**: https://www.terraform.io/docs
- **AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest
- **Terraform CLI**: https://www.terraform.io/cli
- **AWS Documentation**: https://docs.aws.amazon.com/

---

**Terraform Version**: 1.0+  
**AWS Provider Version**: 5.0+  
**Created**: July 2026  
**Last Updated**: July 2026
