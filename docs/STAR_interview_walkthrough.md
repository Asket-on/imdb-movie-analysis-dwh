# STAR Interview Walkthrough - IMDb Movie Analysis DWH Pipeline

Use this structured guide when presenting the project in technical interviews with hiring managers or senior data engineers.

---

## 1. Situation
- **Background**: Modern analytics teams require reliable, reproducible pipelines to transform raw public or transactional data into structured analytical data marts for business intelligence.
- **The Challenge**: Public datasets like IMDb are often messy—containing custom null markers (`\N`), mixed string formats, and high-volume multi-value array fields (e.g., comma-separated genres and director IDs) that cause join fan-outs and query performance degradation if modeled poorly.
- **Goal**: Build a self-contained, enterprise-grade Data Warehouse pipeline that automates daily extraction, cleaning, multi-layer transformation, and data quality testing of IMDb movie datasets.

---

## 2. Task
- Design an end-to-end data architecture capable of running locally via **Docker Compose** (PostgreSQL + Apache Airflow).
- Implement a Python ingestion service that handles large gzipped TSV files without memory exhaustion.
- Architect a modular 3-layer data warehouse in **dbt Core** (`staging`, `intermediate`, `marts`) adhering to Analytics Engineering best practices.
- Implement automated data quality gates and build a deterministic offline test suite.

---

## 3. Action (Engineering Execution)

### A. Data Extraction & Ingestion (`src/ingest_imdb.py`)
- **Avoided Fragile Scraping**: Instead of web scraping HTML pages (which frequently breaks due to UI changes and bot detection), I integrated official daily IMDb compressed TSV archives (`title.basics.tsv.gz`, `title.ratings.tsv.gz`, `title.crew.tsv.gz`).
- **Memory-Efficient Batch Loading**: Used Pandas chunked processing (`chunksize=10000`) combined with SQLAlchemy to stream rows into PostgreSQL staging tables without exceeding container RAM limits.
- **Deterministic Sampling**: Built a `--sample` generator that creates realistic synthetic datasets for offline development and lightning-fast CI/CD unit testing (`pytest`).

### B. Analytical Modeling with dbt Core (`dbt_imdb`)
- **Staging Layer (`stg_imdb__*`)**: Cleaned dirty IMDb null representations (`\N` $\rightarrow$ `NULL`), standardized column naming, and cast raw strings into native integers and numerics using regex validation.
- **Intermediate Layer (`int_movies_with_ratings`)**: Inner joined movie metadata with user vote volumes and left joined crew identifiers. Applied quality filters (retaining feature films, TV series, and documentaries with $\ge 100$ votes) to remove noise.
- **Marts Layer (`mart_*`)**:
  - `mart_genre_analytics`: Utilized PostgreSQL array functions (`string_to_array()` and `lateral unnest()`) to cleanly explode comma-separated genres and compute decade-by-decade weighted average ratings and vote volumes.
  - `mart_director_success`: Aggregated filmographies to calculate career hit ratios (percentage of films with rating $\ge 7.5$) and vote volumes.
  - `mart_yearly_cinema_evolution`: Tracked macro release counts and average runtimes from 1950 to the present.

### C. Orchestration & Quality Assurance (`dags/` & `tests/`)
- **Apache Airflow DAG**: Configured `imdb_daily_dwh_pipeline.py` to run on a daily schedule (`0 4 * * *`). The DAG enforces strict execution boundaries: if data ingestion fails, transformation never runs; if `dbt test` fails on staging, analytical marts are not built.
- **Data Quality Assertions**: Added automated schema tests in `schema.yml` asserting primary key uniqueness, non-null values on critical dimensions, and domain range assertions (ratings bounded between $0.0$ and $10.0$).

---

## 4. Result
- **Deliverable**: Delivered a complete, self-contained Data Engineering portfolio project that can be cloned and deployed by any reviewer with a single command (`make up`).
- **Performance & Reliability**: By switching from web scraping to gzipped TSV streaming and adding chunked loading, pipeline execution time dropped to under 2 minutes locally while guaranteeing 100% reproducibility.
- **Business Impact**: Provide downstream analytical models ready for direct connection to Power BI, Superset, or Metabase without requiring analysts to perform ad-hoc data cleaning.

---

## Common Interview Follow-Up Questions & Answers

### Q: Why did you choose PostgreSQL over BigQuery or Snowflake for this demo?
**A**: For a public portfolio project, PostgreSQL inside Docker Compose allows any hiring manager or recruiter to clone the repository and run `docker-compose up` without needing cloud billing accounts or API keys. Because dbt Core abstracts SQL dialects, migrating this pipeline to Google BigQuery or Snowflake requires changing just a few lines in `profiles.yml`.

### Q: How would you handle incremental updates when the dataset grows to 100M+ rows?
**A**: In dbt, I would change model materializations from `table` / `view` to `incremental`. Using `is_incremental()` macros, we would only filter and process rows where `updated_at >= (select max(updated_at) from {{ this }})` or partition the data warehouse by `release_year`.
