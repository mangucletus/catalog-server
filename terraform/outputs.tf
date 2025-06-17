# Output values to display after terraform apply

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.web.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.web.public_dns
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.postgres.db_name
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.main.id
}

output "cognito_identity_pool_id" {
  description = "Cognito Identity Pool ID"
  value       = aws_cognito_identity_pool.main.id
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_instance.web.public_ip}"
}

output "api_health_check" {
  description = "API health check URL"
  value       = "http://${aws_instance.web.public_ip}/health"
}

output "setup_instructions" {
  description = "Next steps to complete setup"
  value = <<EOF
1. Update frontend/.env with the following values:
   REACT_APP_USER_POOL_ID=${aws_cognito_user_pool.main.id}
   REACT_APP_USER_POOL_CLIENT_ID=${aws_cognito_user_pool_client.main.id}
   REACT_APP_IDENTITY_POOL_ID=${aws_cognito_identity_pool.main.id}
   REACT_APP_API_URL=http://${aws_instance.web.public_ip}

2. Run: cd frontend && npm run build
3. Copy build files to EC2: scp -r build/* ubuntu@${aws_instance.web.public_ip}:/opt/catalog-server/frontend/
4. Access your application at: http://${aws_instance.web.public_ip}
EOF
}