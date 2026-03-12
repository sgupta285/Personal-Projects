terraform {
  required_version = ">= 1.5.0"
}

resource "null_resource" "example" {
  triggers = {
    environment = var.environment
    owner       = var.owner
  }
}
