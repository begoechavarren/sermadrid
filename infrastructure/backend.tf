terraform {
  backend "s3" {
    bucket     = var.aws_s3_bucket_name
    key        = "terraform.tfstate"
    region     = var.aws_region
    access_key = var.aws_access_key
    secret_key = var.aws_secret_key
  }
}
