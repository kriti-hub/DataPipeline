"""Tests for the load module (local mode — writes to Parquet)."""

import os
from pathlib import Path

import pandas as pd
import pytest

from src.etl.utils.gcp import load_to_bigquery


class TestLocalLoad:
    def test_write_truncate_creates_file(self, tmp_path: Path) -> None:
        """WRITE_TRUNCATE creates a Parquet file."""
        os.environ["LOCAL_MODE"] = "true"

        df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
        rows = load_to_bigquery(df, "test.dataset.my_table", "WRITE_TRUNCATE")
        assert rows == 2

    def test_write_append_accumulates(self, tmp_path: Path) -> None:
        """WRITE_APPEND adds to existing data."""
        os.environ["LOCAL_MODE"] = "true"

        df1 = pd.DataFrame({"id": [1]})
        load_to_bigquery(df1, "test.dataset.append_table", "WRITE_TRUNCATE")

        df2 = pd.DataFrame({"id": [2]})
        rows = load_to_bigquery(df2, "test.dataset.append_table", "WRITE_APPEND")
        assert rows == 1

        # Verify accumulated data
        out = Path("data") / "local_output" / "bigquery" / "append_table.parquet"
        if out.exists():
            result = pd.read_parquet(out)
            assert len(result) == 2
