resource "aws_cloudwatch_dashboard" "this" {
  dashboard_name = "${var.name}-platform"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x = 0
        y = 0
        width = 12
        height = 6
        properties = {
          metrics = [["AWS/ECS", "CPUUtilization", "ClusterName", var.name]]
          title   = "ECS CPU"
          stat    = "Average"
        }
      }
    ]
  })
}
