variable "region" {
  description = "AWS region"
  type        = string
}

variable "remote_state_bucket_name" {
  description = "Name of the S3 bucket used for Terraform remote state"
  type        = string
}

variable "input_bucket" {
  description = "Name of the S3 bucket containing input data"
  type        = string
}