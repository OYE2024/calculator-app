# ============================================================================
# VPC OUTPUTS
# ============================================================================

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

# ============================================================================
# SUBNET OUTPUTS
# ============================================================================

output "public_subnet_1_id" {
  description = "ID of public subnet 1"
  value       = aws_subnet.public_1.id
}

output "public_subnet_2_id" {
  description = "ID of public subnet 2"
  value       = aws_subnet.public_2.id
}

output "private_subnet_1_id" {
  description = "ID of private subnet 1"
  value       = aws_subnet.private_1.id
}

output "private_subnet_2_id" {
  description = "ID of private subnet 2"
  value       = aws_subnet.private_2.id
}

# ============================================================================
# DATABASE OUTPUTS
# ============================================================================

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_address" {
  description = "RDS database address (hostname)"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS database port"
  value       = aws_db_instance.main.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "rds_username" {
  description = "RDS database username"
  value       = aws_db_instance.main.username
  sensitive   = false
}

output "rds_engine" {
  description = "RDS database engine"
  value       = aws_db_instance.main.engine
}

output "rds_engine_version" {
  description = "RDS database engine version"
  value       = aws_db_instance.main.engine_version
}

output "rds_instance_class" {
  description = "RDS database instance class"
  value       = aws_db_instance.main.instance_class
}

output "rds_resource_id" {
  description = "RDS database resource ID"
  value       = aws_db_instance.main.resource_id
}

# ============================================================================
# ELASTIC BEANSTALK OUTPUTS
# ============================================================================

output "eb_application_name" {
  description = "Elastic Beanstalk application name"
  value       = aws_elastic_beanstalk_application.main.name
}

output "eb_environment_name" {
  description = "Elastic Beanstalk environment name"
  value       = aws_elastic_beanstalk_environment.main.name
}

output "eb_environment_id" {
  description = "Elastic Beanstalk environment ID"
  value       = aws_elastic_beanstalk_environment.main.id
}

output "eb_cname" {
  description = "Elastic Beanstalk CNAME (application URL)"
  value       = aws_elastic_beanstalk_environment.main.cname
}

output "eb_load_balancer_name" {
  description = "Name of the load balancer"
  value       = aws_elastic_beanstalk_environment.main.load_balancers
}

# ============================================================================
# SECURITY GROUP OUTPUTS
# ============================================================================

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "Application security group ID"
  value       = aws_security_group.app.id
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}

# ============================================================================
# DEPLOYMENT INFORMATION
# ============================================================================

output "deployment_info" {
  description = "Deployment information summary"
  value = {
    application_url = "http://${aws_elastic_beanstalk_environment.main.cname}"
    https_url       = "https://${aws_elastic_beanstalk_environment.main.cname}"
    database_host   = aws_db_instance.main.address
    database_port   = aws_db_instance.main.port
    database_name   = aws_db_instance.main.db_name
    environment     = var.environment
    region          = var.aws_region
  }
}

# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

output "next_steps" {
  description = "Instructions for deploying the application"
  value = <<-EOT
    Infrastructure has been successfully created!

    Next Steps:
    1. Wait 5-10 minutes for EB environment to be fully initialized
    2. Check environment status:
       aws elasticbeanstalk describe-environment-health --environment-name ${aws_elastic_beanstalk_environment.main.name}

    3. Deploy your application:
       cd <project_directory>
       eb init -p python-3.11 ${aws_elastic_beanstalk_application.main.name} -r ${var.aws_region}
       eb use ${aws_elastic_beanstalk_environment.main.name}
       eb deploy

    4. Monitor the deployment:
       eb logs --stream

    5. Open the application:
       eb open

    6. View the application at:
       http://${aws_elastic_beanstalk_environment.main.cname}

    Database Connection Details:
    Host:     ${aws_db_instance.main.address}
    Port:     ${aws_db_instance.main.port}
    Database: ${aws_db_instance.main.db_name}
    Username: ${aws_db_instance.main.username}

    These credentials are automatically passed to the EB environment via environment variables.
  EOT
}
