# ============================================================================
# AWS CONFIGURATION
# ============================================================================

aws_region = "us-east-1"

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

project_name = "calculator-app"
environment  = "dev"

# ============================================================================
# VPC CONFIGURATION
# ============================================================================

vpc_cidr              = "10.0.0.0/16"
public_subnet_1_cidr  = "10.0.1.0/24"
public_subnet_2_cidr  = "10.0.2.0/24"
private_subnet_1_cidr = "10.0.10.0/24"
private_subnet_2_cidr = "10.0.11.0/24"

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# PostgreSQL Version
postgres_version       = "15.3"
postgres_major_version = "15"

# Instance Settings
db_instance_class    = "db.t3.micro"     # Change to db.t3.small or larger for production
db_allocated_storage = 20                # Minimum 20 GB

# Database Credentials
db_name     = "calculator_db"
db_username = "admin"
db_password = "qwerty123!"         

# Backup and HA Configuration
db_multi_az                = false        # Set to true for production
db_backup_retention_days   = 7            # 7 days of backups
db_create_snapshot_on_delete = false      # Set to true for production

# ============================================================================
# ELASTIC BEANSTALK CONFIGURATION
# ============================================================================

# Solution Stack (Python 3.11)
eb_solution_stack = "64bit Amazon Linux 2 v5.8.6 running Python 3.11"

# Instance Configuration
eb_instance_type = "t3.micro"            # Change to t3.small or larger for production

# Scaling Configuration
eb_min_instances = 1                      # Minimum number of instances
eb_max_instances = 3                      # Maximum number of instances

# ============================================================================
# ADDITIONAL TAGS
# ============================================================================

additional_tags = {
  Team        = "Development"
  CostCenter  = "Engineering"
  Application = "CalculatorApp"
}
