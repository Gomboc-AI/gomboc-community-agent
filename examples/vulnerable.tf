# Example: Vulnerable Terraform code
# This file has security issues that Gomboc will detect and fix

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Issue 1: S3 bucket without encryption
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-insecure-bucket-${data.aws_caller_identity.current.account_id}"
  
  # Missing: server_side_encryption_configuration
  # Missing: versioning
  # Missing: public_access_block
}

# Issue 2: Security group too permissive
resource "aws_security_group" "web_sg" {
  name        = "web-sg"
  description = "Web server security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Too permissive!
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Issue 3: RDS without encryption
resource "aws_db_instance" "database" {
  identifier     = "mydb"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  # Missing: storage_encrypted = true
  # Missing: backup_retention_period
  # Missing: multi_az
  
  username = "admin"
  password = "hardcoded-password-123"  # ❌ Exposed in code!
  
  publicly_accessible = true  # ❌ Exposed to internet
}

# Issue 4: Lambda without proper permissions
resource "aws_lambda_function" "processor" {
  filename      = "lambda.zip"
  function_name = "processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  
  # Missing: environment variable encryption
  # Missing: VPC configuration
  # Missing: reserved_concurrent_executions
  
  environment {
    variables = {
      DB_PASSWORD = "secret123"  # ❌ Exposed in code!
    }
  }
}

# Issue 5: IAM role with overly permissive policy
resource "aws_iam_role" "lambda_role" {
  name = "lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"  # ❌ Too permissive!
        Resource = "*"
      }
    ]
  })
}

# Supporting resources
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
}

resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

data "aws_caller_identity" "current" {}

# Outputs (not sensitive)
output "bucket_name" {
  value       = aws_s3_bucket.insecure_bucket.id
  description = "Name of S3 bucket"
}
