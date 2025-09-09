variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "pronas-pcd-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "database_name" {
  description = "RDS database name"
  type        = string
  default     = "pronas_pcd"
}

variable "database_username" {
  description = "RDS master username"
  type        = string
  default     = "pronas_admin"
}

variable "database_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "allowed_ips" {
  description = "Allowed IPs for EKS API access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}