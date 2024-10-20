variable "region" {
  description = "The region to deploy resources to"
  default     = "eu-west-3"
  type        = string
}

variable "remote_state_bucket_name" {
  description = "The name of the S3 bucket to deploy"
  default     = "zenml-tf"
  type        = string
}

variable "dynamo_table_name" {
  description = "The name of the DynamoDB table to deploy"
  default     = "terraform-remote-state-locks"
  type        = string
}

variable "force_destroy" {
  description = "A boolean that indicates all objects should be deleted from the bucket so that the bucket can be destroyed without error"
  default     = true
  type        = bool
}

variable "tags" {
  description = "A map of tags to apply to the bucket"
  type        = map(string)
  default     = {}
}