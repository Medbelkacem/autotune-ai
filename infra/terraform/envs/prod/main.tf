terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.70" }
  }
  backend "s3" {
    bucket         = "autotune-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "autotune-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "autotune-ai"
      Environment = "prod"
      ManagedBy   = "terraform"
      Compliance  = "soc2-iso27001"
    }
  }
}

variable "region" {
  type    = string
  default = "us-east-1"
}

module "vpc" {
  source        = "../../modules/vpc"
  name          = "autotune-prod"
  cidr          = "10.30.0.0/16"
  azs           = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_cidrs  = ["10.30.0.0/20", "10.30.16.0/20", "10.30.32.0/20"]
  private_cidrs = ["10.30.64.0/20", "10.30.80.0/20", "10.30.96.0/20"]
  data_cidrs    = ["10.30.128.0/22", "10.30.132.0/22", "10.30.136.0/22"]
}

module "eks" {
  source          = "../../modules/eks"
  cluster_name    = "autotune-prod"
  cluster_version = "1.30"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  node_groups = {
    general = { instance_types = ["m6i.xlarge"],  min = 3, max = 20, desired = 4 }
    memory  = { instance_types = ["r6i.xlarge"],  min = 0, max = 12, desired = 0 }
    gpu     = { instance_types = ["g5.2xlarge"],  min = 0, max = 4,  desired = 0, taints = [{ key = "nvidia.com/gpu", value = "true", effect = "NO_SCHEDULE" }] }
  }
}

module "rds" {
  source     = "../../modules/rds"
  name       = "autotune-prod"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.data_subnet_ids
  # Aurora Postgres 16 with pgvector; multi-AZ; PITR 35 days
  engine_version = "16.4"
  instance_class = "db.r6g.large"
  min_capacity   = 2
  max_capacity   = 32
}

module "redis" {
  source           = "../../modules/redis"
  name             = "autotune-prod"
  vpc_id           = module.vpc.vpc_id
  subnet_ids       = module.vpc.private_subnet_ids
  node_type        = "cache.r7g.large"
  num_node_groups  = 3
  replicas_per_ng  = 1
  transit_encryption = true
  at_rest_encryption = true
}

module "kafka" {
  source     = "../../modules/kafka"
  name       = "autotune-prod"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  kafka_version   = "3.7.x"
  broker_count    = 3
  broker_type     = "kafka.m7g.large"
  encryption_in_transit_client_broker = "TLS"
}

module "s3" {
  source = "../../modules/s3"
  buckets = {
    artifacts     = { versioning = true,  lifecycle_expiration_days = 365 }
    backups       = { versioning = true,  lifecycle_expiration_days = 2555 }
    telemetry-cold = { versioning = false, lifecycle_expiration_days = 1825 }
  }
}

module "observability" {
  source       = "../../modules/observability"
  cluster_name = module.eks.cluster_name
  grafana_workspace = "autotune-prod"
}
