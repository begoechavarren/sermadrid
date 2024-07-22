provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "app_repository" {
  name = var.ecr_repository_name
}

output "ecr_repository_uri" {
  value = aws_ecr_repository.app_repository.repository_url
}

variable "aws_region" {
  type        = string
  description = "AWS Region"
}

variable "ecr_repository_name" {
  description = "The name of the ECR repository"
}
