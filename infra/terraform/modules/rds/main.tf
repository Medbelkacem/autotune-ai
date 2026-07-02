variable "name"           { type = string }
variable "vpc_id"         { type = string }
variable "subnet_ids"     { type = list(string) }
variable "engine_version" { type = string }
variable "instance_class" { type = string }
variable "min_capacity"   { type = number }
variable "max_capacity"   { type = number }

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-subnets"
  subnet_ids = var.subnet_ids
}

resource "aws_rds_cluster" "aurora_pg" {
  cluster_identifier      = "${var.name}-pg"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = var.engine_version
  database_name           = "autotune"
  master_username         = "autotune"
  manage_master_user_password = true
  db_subnet_group_name    = aws_db_subnet_group.this.name
  storage_encrypted       = true
  backup_retention_period = 35
  preferred_backup_window = "07:00-09:00"
  deletion_protection     = true
  skip_final_snapshot     = false
  final_snapshot_identifier = "${var.name}-final"
  serverlessv2_scaling_configuration {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }
  enabled_cloudwatch_logs_exports = ["postgresql"]
}

resource "aws_rds_cluster_instance" "writer" {
  identifier          = "${var.name}-pg-w"
  cluster_identifier  = aws_rds_cluster.aurora_pg.id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.aurora_pg.engine
  engine_version      = aws_rds_cluster.aurora_pg.engine_version
  publicly_accessible = false
}

resource "aws_rds_cluster_instance" "reader" {
  count               = 1
  identifier          = "${var.name}-pg-r${count.index}"
  cluster_identifier  = aws_rds_cluster.aurora_pg.id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.aurora_pg.engine
  engine_version      = aws_rds_cluster.aurora_pg.engine_version
  publicly_accessible = false
}

output "endpoint" { value = aws_rds_cluster.aurora_pg.endpoint }
output "reader_endpoint" { value = aws_rds_cluster.aurora_pg.reader_endpoint }
