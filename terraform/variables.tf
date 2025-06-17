# Variables for Terraform configuration

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "catalog-server"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"  # Free tier eligible
}

variable "key_pair_name" {
  description = "Name of the AWS key pair for EC2 access"
  type        = string
  default     = "catalog-server-key"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Warning: This allows access from anywhere. Restrict in production!
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "catalog_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  default     = "catalog_pass_change_me"
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "catalog"
}