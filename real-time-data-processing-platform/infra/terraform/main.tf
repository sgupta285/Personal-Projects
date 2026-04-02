terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_dynamodb_table" "entity_state" {
  name         = "${var.project_name}-entity-state"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "entity_id"

  attribute {
    name = "entity_id"
    type = "S"
  }
}

resource "aws_sqs_queue" "dlq" {
  name = "${var.project_name}-dlq"
}

resource "aws_cloudwatch_log_group" "processing" {
  name              = "/aws/${var.project_name}/processing"
  retention_in_days = 14
}

resource "aws_cloudwatch_metric_alarm" "high_backlog" {
  alarm_name          = "${var.project_name}-high-backlog"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "QueueDepth"
  namespace           = "RTDP"
  period              = 60
  statistic           = "Average"
  threshold           = 500
  alarm_description   = "Backlog is above operating threshold"
}
