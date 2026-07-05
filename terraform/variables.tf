# ============================================================================
# AWS PROVIDER VARIABLES
# ============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# ============================================================================
# PROJECT VARIABLES
# ============================================================================

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "calculator-app"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ============================================================================
# VPC VARIABLES
# ============================================================================

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_1_cidr" {
  description = "CIDR block for public subnet 1"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_2_cidr" {
  description = "CIDR block for public subnet 2"
  type        = string
  default     = "10.0.2.0/24"
}

variable "private_subnet_1_cidr" {
  description = "CIDR block for private subnet 1"
  type        = string
  default     = "10.0.10.0/24"
}

variable "private_subnet_2_cidr" {
  description = "CIDR block for private subnet 2"
  type        = string
  default     = "10.0.11.0/24"
}

# ============================================================================
# DATABASE VARIABLES
# ============================================================================

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15.3"
}

variable "postgres_major_version" {
  description = "PostgreSQL major version for parameter group"
  type        = string
  default     = "15"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"

  validation {
    condition     = can(regex("^db\\.", var.db_instance_class))
    error_message = "db_instance_class must start with 'db.'."
  }
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20

  validation {
    condition     = var.db_allocated_storage >= 20
    error_message = "db_allocated_storage must be at least 20 GB."
  }
}

variable "db_name" {
  description = "Initial database name"
  type        = string
  default     = "calculator_db"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_name))
    error_message = "db_name must start with a letter and contain only alphanumerics and underscores."
  }
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
  sensitive   = false

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_username))
    error_message = "db_username must start with a letter and contain only alphanumerics and underscores."
  }
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "db_password must be at least 8 characters."
  }
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

variable "db_backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 7

  validation {
    condition     = var.db_backup_retention_days >= 1 && var.db_backup_retention_days <= 35
    error_message = "db_backup_retention_days must be between 1 and 35."
  }
}

variable "db_create_snapshot_on_delete" {
  description = "Create a final snapshot before deleting RDS"
  type        = bool
  default     = false
}

# ============================================================================
# ELASTIC BEANSTALK VARIABLES
# ============================================================================

variable "eb_solution_stack" {
  description = "Elastic Beanstalk solution stack"
  type        = string
  default     = "64bit Amazon Linux 2 v5.8.6 running Python 3.11"
}

variable "eb_instance_type" {
  description = "EC2 instance type for Elastic Beanstalk"
  type        = string
  default     = "t3.micro"

  validation {
    condition     = can(regex("^[a-z][a-z0-9]*\\.(nano|micro|small|medium|large)$", var.eb_instance_type))
    error_message = "eb_instance_type must be a valid EC2 instance type."
  }
}

variable "eb_min_instances" {
  description = "Minimum number of EC2 instances"
  type        = number
  default     = 1

  validation {
    condition     = var.eb_min_instances >= 1
    error_message = "eb_min_instances must be at least 1."
  }
}

variable "eb_max_instances" {
  description = "Maximum number of EC2 instances"
  type        = number
  default     = 3

  validation {
    condition     = var.eb_max_instances >= 1
    error_message = "eb_max_instances must be at least 1."
  }
}

# ============================================================================
# TAGS
# ============================================================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
