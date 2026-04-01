terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "service" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"
}

resource "aws_s3_bucket" "artifacts" {
  bucket = var.artifact_bucket_name
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ml-serving/api"
  retention_in_days = 14
}
