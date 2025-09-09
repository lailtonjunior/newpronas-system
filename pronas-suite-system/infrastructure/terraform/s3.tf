resource "aws_s3_bucket" "documents" {
  bucket = "${var.cluster_name}-documents-${var.environment}"

  tags = {
    Name        = "${var.cluster_name}-documents"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "ml_models" {
  bucket = "${var.cluster_name}-ml-models-${var.environment}"

  tags = {
    Name        = "${var.cluster_name}-ml-models"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    id = "archive-old-documents"

    filter {
      prefix = "archives/"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }

    status = "Enabled"
  }
}