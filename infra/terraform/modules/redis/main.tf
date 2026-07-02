variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "node_type" { type = string }
variable "num_node_groups" { type = number }
variable "replicas_per_ng" { type = number }
variable "transit_encryption" { type = bool, default = true }
variable "at_rest_encryption" { type = bool, default = true }

resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name}-subnets"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "${var.name}-redis"
  description                = "AutoTune primary Redis"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = var.node_type
  parameter_group_name       = "default.redis7.cluster.on"
  automatic_failover_enabled = true
  num_node_groups            = var.num_node_groups
  replicas_per_node_group    = var.replicas_per_ng
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  transit_encryption_enabled = var.transit_encryption
  at_rest_encryption_enabled = var.at_rest_encryption
  auto_minor_version_upgrade = true
}
