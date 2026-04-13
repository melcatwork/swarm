# Sample Terraform configuration for testing IaC upload API

terraform {
  required_version = ">= 1.0"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = "true"
  enable_dns_support   = "true"

  tags = {
    Name = "main-vpc"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = "true"

  tags = {
    Name = "public-subnet"
  }
}

# Private Subnet
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"

  tags = {
    Name = "private-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# Security Group - Web
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}

# Security Group - Database
resource "aws_security_group" "database" {
  name        = "database-sg"
  description = "Security group for database"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from web tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  tags = {
    Name = "database-sg"
  }
}

# IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "ec2-web-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "ec2-web-role"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"

  tags = {
    Name = "data-bucket"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# EC2 Instance
resource "aws_instance" "web" {
  ami                         = "ami-0c55b159cbfafe1f0"
  instance_type               = "t3.medium"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  iam_instance_profile        = aws_iam_role.ec2_role.name
  associate_public_ip_address = "true"

  tags = {
    Name = "web-server"
  }
}

# Application Load Balancer
resource "aws_lb" "web" {
  name               = "web-alb"
  internal           = "false"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web.id]
  subnets            = [aws_subnet.public.id]

  tags = {
    Name = "web-alb"
  }
}

# RDS Database
resource "aws_rds_instance" "postgres" {
  identifier              = "postgres-db"
  engine                  = "postgres"
  engine_version          = "14.7"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  storage_encrypted       = "true"
  db_name                 = "mydb"
  username                = "admin"
  password                = "ChangeMeInProduction123!"
  vpc_security_group_ids  = [aws_security_group.database.id]
  db_subnet_group_name    = "my-db-subnet-group"
  publicly_accessible     = "false"
  skip_final_snapshot     = true

  tags = {
    Name = "postgres-db"
  }
}
