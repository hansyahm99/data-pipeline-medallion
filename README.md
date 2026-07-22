# data-pipeline-medallion
# Data Engineering

Building the modern data stack: ETL pipelines, workflow orchestration, and SQL-driven transformations using Python, PySpark, dbt & Airflow.

## Architecture

This project follows the **Medallion Architecture** pattern (Bronze → Silver → Gold), orchestrated end-to-end from raw ingestion to business-ready data.

```
Data Sources          Ingestion              Orchestration
(Files, APIs,    →    (Python &         →     (Airflow
 Database)             PySpark)                 DAG schedule)
                                                     │
                                                     ▼
   Bronze          →       Silver          →       Gold
(Raw data as-is)      (Cleaned, deduped)      (Business-ready,
 dbt: staging          dbt: intermediate       dbt: marts,
                                                Snowflake)
                                                     
```

### Layers

| Layer | Purpose | Location |
|---|---|---|
| **Bronze** | Raw data ingested as-is, no transformation | `models/bronze/` (dbt staging) |
| **Silver** | Cleaned, deduplicated, standardized schema | `models/silver/` (dbt intermediate) |
| **Gold** | Aggregated, dimensional models ready for consumption | `models/gold/` (dbt marts) |

## Tech Stack

- **Ingestion & Processing:** Python, PySpark
- **Orchestration:** Apache Airflow
- **Transformation & Modeling:** dbt
- **Warehouse:** Snowflake

## Project Structure

```
data-engineering/
├── ingestion/          # Python & PySpark ingestion scripts
├── dags/                # Airflow DAG definitions
├── dbt_project/
│   └── models/
│       ├── bronze/      # Raw staging models
│       ├── silver/      # Cleaned intermediate models
│       └── gold/        # Business-ready mart models
├── tests/               # dbt tests / data quality checks
├── docs/                 # Architecture diagrams & documentation
└── docker-compose.yml     # Local environment setup
```

## Getting Started

```bash
# Clone the repo
git clone <repo-url>
cd data-engineering

# Spin up local environment
docker-compose up -d

# Run dbt models
cd dbt_project
dbt run
dbt test
```

## Roadmap

- [ ] Add data quality checks (dbt tests / Great Expectations)
- [ ] Add CI/CD pipeline for automated testing & deployment
- [ ] Add streaming ingestion example
- [ ] Add Infrastructure as Code (Terraform) for cloud resources
