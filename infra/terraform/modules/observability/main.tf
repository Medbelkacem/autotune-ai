variable "cluster_name"      { type = string }
variable "grafana_workspace" { type = string }

resource "aws_grafana_workspace" "this" {
  name                     = var.grafana_workspace
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  data_sources             = ["PROMETHEUS", "CLOUDWATCH", "XRAY"]
}

resource "aws_prometheus_workspace" "this" {
  alias = "autotune-${var.cluster_name}"
}
