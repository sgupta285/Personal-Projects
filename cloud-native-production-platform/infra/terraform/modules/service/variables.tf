variable "name" { type = string }
variable "cluster_name" { type = string }
variable "container_image" { type = string }
variable "container_port" { type = number }
variable "desired_count" { type = number }
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "environment" { type = map(string) }
