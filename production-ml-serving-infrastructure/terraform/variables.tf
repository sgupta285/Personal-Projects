variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "repository_name" {
  type    = string
  default = "production-ml-serving-infrastructure"
}

variable "artifact_bucket_name" {
  type = string
}
