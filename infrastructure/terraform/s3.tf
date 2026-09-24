resource "aws_s3_bucket" "loan_documents" {
  bucket = "loan-assessment-documents-588319087184-ap-south-1"

  tags = {
    Name = "loan-assessment-private-documents"
  }
}

resource "aws_s3_bucket_public_access_block" "loan_documents" {
  bucket = aws_s3_bucket.loan_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "loan_documents" {
  bucket = aws_s3_bucket.loan_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "loan_documents" {
  bucket = aws_s3_bucket.loan_documents.id

  versioning_configuration {
    status = "Enabled"
  }
}