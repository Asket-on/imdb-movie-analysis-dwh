import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def get_connection_string() -> str:
    """Build PostgreSQL connection string from environment variables."""
    user = os.environ.get("POSTGRES_USER", "imdb_user")
    password = os.environ.get("POSTGRES_PASSWORD", "imdb_password")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "imdb_dwh")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def get_engine() -> Engine:
    """Create and return SQLAlchemy engine."""
    conn_str = get_connection_string()
    return create_engine(conn_str, pool_pre_ping=True)


def init_schemas(engine: Engine) -> None:
    """Create necessary analytical schemas if they do not exist."""
    schemas = ["raw_imdb", "dbt_staging", "dbt_marts"]
    with engine.begin() as conn:
        for schema in schemas:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
            logger.info(f"Initialized schema: {schema}")
