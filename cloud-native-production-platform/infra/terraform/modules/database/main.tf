resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnets"
  subnet_ids = var.private_subnet_ids
}

resource "aws_db_instance" "this" {
  identifier             = "${var.name}-postgres"
  engine                 = "postgres"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  db_name                = var.db_name
  username               = var.username
  password               = var.password
  skip_final_snapshot    = true
  publicly_accessible    = false
  db_subnet_group_name   = aws_db_subnet_group.this.name
}
