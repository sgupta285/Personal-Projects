terraform {
  required_version = ">= 1.6.0"
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

module "network" {
  source               = "../../modules/network"
  name                 = var.name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  azs                  = var.azs
}

module "database" {
  source             = "../../modules/database"
  name               = var.name
  private_subnet_ids = module.network.private_subnet_ids
  username           = var.db_username
  password           = var.db_password
  db_name            = var.db_name
}

module "gateway_service" {
  source             = "../../modules/service"
  name               = "${var.name}-gateway"
  cluster_name       = "${var.name}-cluster"
  container_image    = var.gateway_image
  container_port     = 8000
  desired_count      = var.gateway_desired_count
  subnet_ids         = module.network.public_subnet_ids
  security_group_ids = []
  environment = {
    CATALOG_URL = "http://catalog.internal:8001"
    ORDERS_URL  = "http://orders.internal:8002"
  }
}

module "observability" {
  source = "../../modules/observability"
  name   = var.name
}
