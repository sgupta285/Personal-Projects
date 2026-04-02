terraform {
  required_version = ">= 1.5.0"
}

provider "aws" {
  region = var.aws_region
}

resource "aws_kms_key" "service_key" {
  description             = "CMK for Secure Data Processing Service"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_secretsmanager_secret" "service_secret" {
  name = "secure-data-processing-service/app"
}

output "kms_key_arn" {
  value = aws_kms_key.service_key.arn
}
