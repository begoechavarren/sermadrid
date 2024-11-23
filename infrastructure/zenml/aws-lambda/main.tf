terraform {
  required_version = ">= 1.0"
  
  backend "s3" {
    key = "zenml/lambda/terraform.tfstate"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Import remote state from aws-modular to get ECR repository and other resources
data "terraform_remote_state" "aws_modular" {
  backend = "s3"
  
  config = {
    bucket = var.remote_state_bucket_name
    key    = "zenml/aws-modular/terraform.tfstate"
    region = var.region
  }
}

# Lambda Execution Role
resource "aws_iam_role" "lambda_role" {
  name = "zenml_pipeline_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Policy to allow Lambda to interact with ECR
resource "aws_iam_role_policy" "lambda_ecr" {
  name = "zenml_pipeline_lambda_ecr_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      }
    ]
  })
}

# Policy to allow Lambda to read from S3
resource "aws_iam_role_policy" "lambda_s3" {
  name = "zenml_pipeline_lambda_s3_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.input_bucket}",
          "arn:aws:s3:::${var.input_bucket}/sermadrid/data/input/*"
        ]
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "zenml_pipeline" {
  function_name = "zenml-pipeline-trigger"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = data.terraform_remote_state.aws_modular.outputs.container_registry_uri
  timeout       = 900  # 15 minutes
  memory_size   = 1024

  environment {
    variables = {
      S3_INPUT_PATH = "sermadrid/data/input/"
      # TODO: Add other environment variables as needed
    }
  }
}

# S3 Event trigger
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.input_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.zenml_pipeline.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "sermadrid/data/input/"
  }
}

# Allow S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.zenml_pipeline.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.input_bucket}"
}