variable "buckets" {
  type = map(object({
    versioning                = bool
    lifecycle_expiration_days = number
  }))
}

resource "aws_s3_bucket" "this" {
  for_each = var.buckets
  bucket   = "autotune-${each.key}"
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "v" {
  for_each = { for k, v in var.buckets : k => v if v.versioning }
  bucket   = aws_s3_bucket.this[each.key].id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sse" {
  for_each = aws_s3_bucket.this
  bucket   = each.value.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  for_each                = aws_s3_bucket.this
  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "lc" {
  for_each = var.buckets
  bucket   = aws_s3_bucket.this[each.key].id
  rule {
    id     = "retention"
    status = "Enabled"
    expiration { days = each.value.lifecycle_expiration_days }
  }
}
