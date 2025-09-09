resource "aws_db_subnet_group" "main" {
  name       = "${var.cluster_name}-db-subnet"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.cluster_name} DB subnet group"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.cluster_name}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-rds-sg"
    Environment = var.environment
  }
}

resource "aws_db_instance" "main" {
  identifier = "${var.cluster_name}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  storage_type          = "gp3"

  db_name  = var.database_name
  username = var.database_username
  password = var.database_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.cluster_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = {
    Name = "${var.cluster_name}-database"
    Environment = var.environment
  }
}

resource "aws_db_instance" "read_replica" {
  identifier = "${var.cluster_name}-db-replica"
  
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = "db.r6g.large"

  tags = {
    Name = "${var.cluster_name}-database-replica"
    Environment = var.environment
  }
}