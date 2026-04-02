output "dynamodb_table_name" {
  value = aws_dynamodb_table.entity_state.name
}

output "dlq_name" {
  value = aws_sqs_queue.dlq.name
}
