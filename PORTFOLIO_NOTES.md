# Portfolio Notes - IMDb Movie Analysis Data Warehouse Pipeline

## Quick Overview for CV / Resume
- **Project Title**: End-to-End IMDb Movie Analysis Data Warehouse Pipeline
- **Role**: Data Engineer / Analytics Engineer
- **Tech Stack**: Python, PostgreSQL, dbt Core, Apache Airflow, Docker Compose, SQL, PyTest
- **Target Repository**: https://github.com/Asket-on/imdb-movie-analysis-dwh (or local folder `projects/imdb_movie_analysis`)

---

## 5 Resume Bullet Points (English & German)

### English (International Market)
- **Architected and deployed an end-to-end Data Engineering pipeline** orchestrating daily ingestion, cleaning, and analytical modeling of 1M+ movie records using **Python, PostgreSQL, dbt Core, and Apache Airflow** inside Docker.
- **Engineered a resilient batch extraction module** utilizing chunked streaming of compressed TSV archives (`.tsv.gz`), replacing fragile HTML web scraping and eliminating API rate-limiting bottlenecks.
- **Implemented a modular 3-layer dbt analytical warehouse** (`staging`, `intermediate`, `marts`), utilizing SQL unnesting and window functions to deliver performant data marts for genre performance and director career analytics.
- **Integrated automated Data Quality testing gates** in dbt and Airflow, enforcing primary key uniqueness, referential integrity, and domain constraints across 100% of analytical tables.
- **Designed a deterministic sampling generator (`--sample`)**, enabling offline unit testing (`pytest`) and instant CI/CD pipeline verification with zero network dependencies.

### German (DACH Market / Lebenslauf)
- **Konzeption und Implementierung einer skalierbaren Data-Warehouse-Pipeline** zur automatisierten Verarbeitung und Analyse von über 1 Mio. IMDb-Datensätzen unter Einsatz von **Python, PostgreSQL, dbt Core und Apache Airflow** in Docker.
- **Entwicklung eines robusten Extraktionsmoduls** für komprimierte TSV-Archive mittels Batch-Streaming, wodurch fehleranfälliges Web Scraping und Netzwerk-Engpässe eliminiert wurden.
- **Modellierung einer 3-schichtigen analytischen DWH-Architektur** (Staging, Intermediate, Data Marts) in **dbt Core**, optimiert für BI-Abfragen zu Filmgenres und Regisseur-Erfolgsmetriken.
- **Implementierung automatisierter Data-Quality-Tests** (Null-Checks, Primärschlüsselincongruenz und referenzielle Integrität) in dbt zur Sicherstellung höchster Datenkonsistenz vor dem BI-Export.
- **Erstellung einer automatisierten Testumgebung** inkl. deterministischem Datengenerator und **PyTest**-Unit-Tests zur lückenlosen Offline-Validierung der ETL-Logik.

---

## Architectural Highlights for Technical Interviews
1. **Separation of Concerns**: Ingestion layer (`src/ingest_imdb.py`) is decoupled from transformation logic (`dbt_imdb`), allowing independent scaling or switching warehouse engines (e.g., migration from Postgres to BigQuery).
2. **Handling Dirty Data**: IMDb source files use `\N` for null values. The Python extractor scrubs text fields, while dbt staging models (`stg_imdb__*`) apply strict SQL type casting and regex validation for release years and runtimes.
3. **Idempotent Scheduling**: Airflow DAGs (`imdb_daily_dwh_pipeline.py`) execute clean table replacements/upserts with bounded retry logic, preventing duplicate row accumulation.
