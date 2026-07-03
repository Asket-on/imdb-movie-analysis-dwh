import argparse
import gzip
import io
import logging
import os
from typing import Dict, Optional
import numpy as np
import pandas as pd
import requests
from sqlalchemy.engine import Engine

try:
    from src.db import get_engine, init_schemas
except ImportError:
    from db import get_engine, init_schemas

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

IMDB_BASE_URL = "https://datasets.imdbws.com"
DATASETS = {
    "title_basics": "title.basics.tsv.gz",
    "title_ratings": "title.ratings.tsv.gz",
    "title_crew": "title.crew.tsv.gz",
}


def clean_imdb_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean standard IMDb TSV null representations ('\\N') and whitespace."""
    # Replace IMDb null marker '\N' with NaN
    df = df.replace(to_replace=r"^\\N$", value=np.nan, regex=True)
    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("nan", np.nan)
        df[col] = df[col].replace("None", np.nan)
    return df


def generate_sample_data(num_movies: int = 1000) -> Dict[str, pd.DataFrame]:
    """Generate high-quality deterministic synthetic IMDb sample datasets for offline testing/demo."""
    logger.info(f"Generating synthetic sample datasets ({num_movies} movies)...")
    np.random.seed(42)

    genres_list = [
        "Action,Sci-Fi", "Drama", "Comedy", "Crime,Drama", "Adventure,Drama,Sci-Fi",
        "Animation,Adventure,Family", "Horror,Mystery,Thriller", "Biography,Drama,History",
        "Comedy,Romance", "Action,Adventure,Fantasy", "Documentary", "Action,Thriller"
    ]
    
    directors_pool = [
        "nm0000233", "nm0000229", "nm0634240", "nm0000186", "nm0000338",
        "nm0881279", "nm0001104", "nm0000216", "nm0905152", "nm0000318"
    ]
    writers_pool = [
        "nm0000233,nm0634240", "nm0000229", "nm0881279", "nm0000186", "nm0000338,nm0001104",
        "nm0905152", "nm0000318", "nm0000216,nm0000233", "nm0634240,nm0881279"
    ]

    tconsts = [f"tt{1000000 + i:07d}" for i in range(num_movies)]
    
    # Title basics
    basics_data = {
        "tconst": tconsts,
        "titleType": np.random.choice(["movie", "tvSeries", "short", "documentary"], size=num_movies, p=[0.7, 0.15, 0.05, 0.1]),
        "primaryTitle": [f"Sample Movie Title {i}" for i in range(num_movies)],
        "originalTitle": [f"Sample Movie Title {i}" for i in range(num_movies)],
        "isAdult": np.random.choice(["0", "1"], size=num_movies, p=[0.98, 0.02]),
        "startYear": np.random.randint(1950, 2025, size=num_movies).astype(str),
        "endYear": ["\\N"] * num_movies,
        "runtimeMinutes": np.random.randint(70, 190, size=num_movies).astype(str),
        "genres": np.random.choice(genres_list, size=num_movies)
    }
    df_basics = pd.DataFrame(basics_data)
    # Make a few random nulls for testing
    df_basics.loc[0:10, "runtimeMinutes"] = "\\N"
    df_basics.loc[11:20, "genres"] = "\\N"

    # Title ratings
    ratings_data = {
        "tconst": tconsts,
        "averageRating": np.round(np.random.uniform(3.5, 9.5, size=num_movies), 1),
        "numVotes": np.random.exponential(scale=50000, size=num_movies).astype(int) + 100
    }
    df_ratings = pd.DataFrame(ratings_data)

    # Title crew
    crew_data = {
        "tconst": tconsts,
        "directors": np.random.choice(directors_pool, size=num_movies),
        "writers": np.random.choice(writers_pool, size=num_movies)
    }
    df_crew = pd.DataFrame(crew_data)

    return {
        "title_basics": clean_imdb_dataframe(df_basics),
        "title_ratings": clean_imdb_dataframe(df_ratings),
        "title_crew": clean_imdb_dataframe(df_crew),
    }


def download_imdb_dataset(dataset_name: str, filename: str, data_dir: str, limit_rows: Optional[int] = None) -> pd.DataFrame:
    """Download and parse a gzipped TSV file from IMDb."""
    url = f"{IMDB_BASE_URL}/{filename}"
    local_path = os.path.join(data_dir, filename)

    if not os.path.exists(local_path):
        logger.info(f"Downloading live dataset from {url} to {local_path}...")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        os.makedirs(data_dir, exist_ok=True)
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded {filename} successfully.")
    else:
        logger.info(f"Using cached local archive: {local_path}")

    logger.info(f"Reading TSV archive: {filename} (limit={limit_rows})...")
    with gzip.open(local_path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f, sep="\t", nrows=limit_rows, dtype=str, na_values=["\\N"], keep_default_na=True)
    
    return clean_imdb_dataframe(df)


def ingest_to_postgres(df: pd.DataFrame, table_name: str, engine: Engine, schema: str = "raw_imdb") -> None:
    """Load DataFrame into PostgreSQL staging schema using batch chunks."""
    logger.info(f"Loading {len(df)} rows into {schema}.{table_name}...")
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )
    logger.info(f"Successfully loaded {schema}.{table_name}.")


def run_ingestion(sample: bool = False, data_dir: str = "data", limit_rows: Optional[int] = None) -> None:
    """Orchestrate data extraction, cleaning, and loading into PostgreSQL."""
    engine = get_engine()
    init_schemas(engine)

    if sample:
        datasets = generate_sample_data(num_movies=limit_rows or 1000)
    else:
        datasets = {}
        for name, filename in DATASETS.items():
            datasets[name] = download_imdb_dataset(name, filename, data_dir, limit_rows=limit_rows)

    for table_name, df in datasets.items():
        ingest_to_postgres(df, table_name, engine, schema="raw_imdb")

    logger.info("IMDb data ingestion completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IMDb Data Ingestion Service")
    parser.add_argument("--sample", action="store_true", help="Generate synthetic sample data instead of downloading")
    parser.add_argument("--data-dir", default="data", help="Directory to store downloaded TSV archives")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows to ingest (for quick testing)")
    args = parser.parse_args()

    run_ingestion(sample=args.sample, data_dir=args.data_dir, limit_rows=args.limit)
