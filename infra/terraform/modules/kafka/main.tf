variable "name"       { type = string }
variable "vpc_id"     { type = string }
variable "subnet_ids" { type = list(string) }
variable "kafka_version"                     { type = string }
variable "broker_count"                      { type = number }
variable "broker_type"                       { type = string }
variable "encryption_in_transit_client_broker" { type = string }

resource "aws_msk_cluster" "this" {
  cluster_name           = var.name
  kafka_version          = var.kafka_version
  number_of_broker_nodes = var.broker_count

  broker_node_group_info {
    instance_type   = var.broker_type
    client_subnets  = var.subnet_ids
    storage_info {
      ebs_storage_info { volume_size = 1000 }
    }
  }
  encryption_info {
    encryption_in_transit {
      client_broker = var.encryption_in_transit_client_broker
      in_cluster    = true
    }
  }
  logging_info {
    broker_logs {
      cloudwatch_logs { enabled = true, log_group = "/msk/${var.name}" }
    }
  }
}
