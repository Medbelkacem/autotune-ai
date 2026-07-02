# AutoTune AI — Terraform (AWS)

Production infrastructure. Provisions:

- VPC (3 AZs, public/private/data subnets)
- EKS 1.30 cluster with managed node groups (general + gpu)
- RDS Aurora Postgres 16 (with pgvector) + Aurora Serverless v2 read replicas
- ElastiCache Redis (cluster mode)
- MSK (Kafka) 3-broker across AZs
- Amazon MQ (RabbitMQ) HA pair
- S3 buckets (artifacts, backups, telemetry-cold)
- KMS keys (per-service)
- Route 53 + ACM certs
- WAFv2 + CloudFront in front of API + web
- Secrets Manager + External Secrets Operator
- CloudWatch + OpenTelemetry export to managed Grafana

## Layout

```
terraform/
├── envs/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── modules/
    ├── vpc/
    ├── eks/
    ├── rds/
    ├── redis/
    ├── kafka/
    ├── s3/
    └── observability/
```

Do NOT `apply` any environment without a peer-reviewed plan.
