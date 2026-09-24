resource "aws_ssm_parameter" "db_host" {
  name  = "/loan-assessment/DB_HOST"
  type  = "String"
  value = aws_db_instance.loan_db.address

  tags = {
    Name = "loan-assessment-db-host"
  }
}

resource "aws_ssm_parameter" "db_name" {
  name  = "/loan-assessment/DB_NAME"
  type  = "String"
  value = aws_db_instance.loan_db.db_name

  tags = {
    Name = "loan-assessment-db-name"
  }
}

resource "aws_ssm_parameter" "db_user" {
  name  = "/loan-assessment/DB_USER"
  type  = "String"
  value = aws_db_instance.loan_db.username

  tags = {
    Name = "loan-assessment-db-user"
  }
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/loan-assessment/DB_PASSWORD"
  type  = "SecureString"
  value = var.db_password

  tags = {
    Name = "loan-assessment-db-password"
  }
}
resource "aws_ssm_parameter" "s3_bucket_name" {
  name  = "/loan-assessment/S3_BUCKET_NAME"
  type  = "String"
  value = aws_s3_bucket.loan_documents.bucket

  tags = {
    Name = "loan-assessment-s3-bucket"
  }
}