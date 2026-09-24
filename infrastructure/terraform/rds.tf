resource "aws_db_instance" "loan_db" {
  identifier = "loan-assessment-db"

  engine         = "postgres"
  engine_version = "18"

  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 20
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "loan_db"
  username = "loan_user"
  password = var.db_password

  db_subnet_group_name = aws_db_subnet_group.loan_db.name
  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false

  backup_retention_period = 0
  skip_final_snapshot     = true

  deletion_protection = false

  tags = {
    Name = "loan-assessment-db"
  }
}