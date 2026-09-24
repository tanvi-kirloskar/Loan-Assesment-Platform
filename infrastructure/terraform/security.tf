# ---------------------------------------------------------
# EC2 Security Group
# ---------------------------------------------------------

resource "aws_security_group" "ec2" {
  name        = "loan-ec2-sg"
  description = "Security group for loan assessment EC2"
  vpc_id      = aws_vpc.loan_vpc.id

  # HTTP from the internet
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS - needed later when we configure TLS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "loan-ec2-sg"
  }
}


# ---------------------------------------------------------
# RDS Security Group
# ---------------------------------------------------------

resource "aws_security_group" "rds" {
  name        = "loan-rds-sg"
  description = "Security group for loan assessment RDS"
  vpc_id      = aws_vpc.loan_vpc.id

  # PostgreSQL ONLY from EC2
  ingress {
    description     = "PostgreSQL from EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "loan-rds-sg"
  }
}