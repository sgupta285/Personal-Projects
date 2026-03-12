output "vpc_id" { value = module.network.vpc_id }
output "db_endpoint" { value = module.database.endpoint }
output "dashboard_name" { value = module.observability.dashboard_name }
