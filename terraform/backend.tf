# S3 Backend configuration for storing Terraform state
# This ensures state is shared and prevents resource recreation

terraform {
  # Comment this block out for FIRST RUN, then uncomment after S3 bucket is created
  backend "s3" {
    bucket = "catalog-server-terraform-state-mangucletus-4523"
    key    = "terraform/terraform.tfstate"
    region = "eu-west-1"
    
    # Disable locking as requested
    # dynamodb_table = "terraform-locks"  # Commented out - no locking
  }
}

# S3 bucket for storing Terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "catalog-server-terraform-state-mangucletus-4523"

  # Prevent accidental deletion of this S3 bucket
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State Store"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Enable versioning on the S3 bucket
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption for the S3 bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access to the S3 bucket
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}