import numpy as np
import pandas as pd
import pytest
from src.ingest_imdb import clean_imdb_dataframe, generate_sample_data


def test_clean_imdb_dataframe():
    raw_data = {
        "tconst": ["tt0000001", "tt0000002", "tt0000003 "],
        "titleType": ["movie", "\\N", "short"],
        "runtimeMinutes": ["100", "nan", "None"]
    }
    df = pd.DataFrame(raw_data)
    cleaned = clean_imdb_dataframe(df)

    # Verify \N is replaced by NaN
    assert pd.isna(cleaned.loc[1, "titleType"]), "Expected \\N to be replaced by NaN"
    # Verify string 'nan' and 'None' are replaced by NaN
    assert pd.isna(cleaned.loc[1, "runtimeMinutes"]), "Expected string 'nan' to be NaN"
    assert pd.isna(cleaned.loc[2, "runtimeMinutes"]), "Expected string 'None' to be NaN"
    # Verify whitespace stripped
    assert cleaned.loc[2, "tconst"] == "tt0000003", "Expected trailing whitespace to be stripped"


def test_generate_sample_data():
    sample_size = 500
    datasets = generate_sample_data(num_movies=sample_size)

    assert "title_basics" in datasets
    assert "title_ratings" in datasets
    assert "title_crew" in datasets

    df_basics = datasets["title_basics"]
    assert len(df_basics) == sample_size
    assert "tconst" in df_basics.columns
    assert "primaryTitle" in df_basics.columns
    assert "genres" in df_basics.columns
    assert df_basics["tconst"].iloc[0].startswith("tt")

    df_ratings = datasets["title_ratings"]
    assert len(df_ratings) == sample_size
    assert "averageRating" in df_ratings.columns
    assert "numVotes" in df_ratings.columns
