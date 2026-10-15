"""
test_data.py — Tes unit untuk data_loader (Fase 1, Bagian 8)
=============================================================
Tes ini memverifikasi:
  - CSV dimuat dengan benar (sep=";", dtype=str)
  - Awalan kutip tunggal dibersihkan
  - Tanggal diparsing dengan format eksplisit
  - Kolom wajib ada setelah load
  - Error yang tepat jika data_dir tidak ada / tidak ada CSV
  - Profiling menghasilkan angka yang masuk akal

Jalankan: pytest tests/test_data.py -v
"""

import json
import textwrap
from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

SAMPLE_CSV_CONTENT = textwrap.dedent("""\
    original_id;title;body;language;entities;source_name;date_published
    '001;Article One;Body of article one.;'en;;Source A;15/10/2026 08.30.00
    '002;Article Two;Body of article two.;'ms;;Source B;14/10/2026 09.00.00
    '001;Article One;Body of article one.;'en;;Source A;15/10/2026 08.30.00
""")


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    """Buat file CSV sementara dengan konten sampel."""
    csv_file = tmp_path / "Maybank_sample_TEST123.csv"
    csv_file.write_text(SAMPLE_CSV_CONTENT, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_dir(sample_csv_path: Path) -> Path:
    """Kembalikan direktori yang berisi file CSV sampel."""
    return sample_csv_path.parent


# ──────────────────────────────────────────────────────────────
# Test: load_csv
# ──────────────────────────────────────────────────────────────

class TestLoadCsv:
    def test_loads_correct_row_count(self, sample_csv_path):
        from src.data_loader import load_csv
        df = load_csv(sample_csv_path)
        # CSV sampel punya 3 baris data
        assert len(df) == 3

    def test_required_columns_present(self, sample_csv_path):
        from src.data_loader import load_csv
        from src.config import REQUIRED_COLUMNS
        df = load_csv(sample_csv_path)
        for col in REQUIRED_COLUMNS:
            assert col in df.columns, f"Kolom wajib hilang: {col}"

    def test_source_file_column_added(self, sample_csv_path):
        from src.data_loader import load_csv
        df = load_csv(sample_csv_path)
        assert "source_file" in df.columns
        assert df["source_file"].iloc[0] == sample_csv_path.name

    def test_leading_quote_stripped_language(self, sample_csv_path):
        """Awalan kutip tunggal pada kolom `language` harus dihapus."""
        from src.data_loader import load_csv
        df = load_csv(sample_csv_path)
        # Nilai asli "'en" dan "'ms" → "en" dan "ms"
        assert not df["language"].dropna().str.startswith("'").any(), (
            "Awalan kutip tunggal masih ada di kolom 'language'"
        )
        assert "en" in df["language"].values
        assert "ms" in df["language"].values

    def test_leading_quote_stripped_original_id(self, sample_csv_path):
        """Awalan kutip tunggal pada `original_id` harus dihapus."""
        from src.data_loader import load_csv
        df = load_csv(sample_csv_path)
        assert not df["original_id"].dropna().str.startswith("'").any()
        assert "001" in df["original_id"].values

    def test_date_parsed(self, sample_csv_path):
        """Kolom `date_published_parsed` harus bertipe datetime."""
        from src.data_loader import load_csv
        df = load_csv(sample_csv_path)
        assert "date_published_parsed" in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df["date_published_parsed"])
        # Tidak ada NaT pada baris yang format-nya benar
        assert df["date_published_parsed"].notna().all()

    def test_all_columns_string_dtype(self, sample_csv_path):
        """Kolom CSV asli harus dibaca sebagai string."""
        from src.data_loader import load_csv
        df = load_csv(sample_csv_path)
        # Kolom teks utama harus object (string)
        for col in ("title", "body", "original_id", "language"):
            assert df[col].dtype == object, f"Kolom '{col}' bukan string: {df[col].dtype}"


# ──────────────────────────────────────────────────────────────
# Test: load_all_csvs
# ──────────────────────────────────────────────────────────────

class TestLoadAllCsvs:
    def test_loads_from_directory(self, sample_dir):
        from src.data_loader import load_all_csvs
        df = load_all_csvs(data_dir=sample_dir)
        assert len(df) == 3

    def test_raises_if_dir_not_found(self, tmp_path):
        from src.data_loader import load_all_csvs
        nonexistent = tmp_path / "not_here"
        with pytest.raises(FileNotFoundError, match="DATA_DIR"):
            load_all_csvs(data_dir=nonexistent)

    def test_raises_if_no_csv(self, tmp_path):
        from src.data_loader import load_all_csvs
        # Direktori ada tapi tidak ada file .csv
        (tmp_path / "readme.txt").write_text("hello")
        with pytest.raises(FileNotFoundError):
            load_all_csvs(data_dir=tmp_path)

    def test_multiple_csvs_concatenated(self, tmp_path):
        """Dua file CSV harus digabung menjadi satu DataFrame."""
        from src.data_loader import load_all_csvs

        content_a = (
            "original_id;title;body;language;entities;source_name;date_published\n"
            "A1;TitleA;BodyA;en;;SrcA;15/10/2026 08.00.00\n"
        )
        content_b = (
            "original_id;title;body;language;entities;source_name;date_published\n"
            "B1;TitleB;BodyB;ms;;SrcB;14/10/2026 09.00.00\n"
        )
        (tmp_path / "file_a.csv").write_text(content_a, encoding="utf-8")
        (tmp_path / "file_b.csv").write_text(content_b, encoding="utf-8")

        df = load_all_csvs(data_dir=tmp_path)
        assert len(df) == 2
        assert set(df["original_id"]) == {"A1", "B1"}

    def test_returns_dataframe(self, sample_dir):
        from src.data_loader import load_all_csvs
        df = load_all_csvs(data_dir=sample_dir)
        assert isinstance(df, pd.DataFrame)


# ──────────────────────────────────────────────────────────────
# Test: profiling (unit-level)
# ──────────────────────────────────────────────────────────────

class TestProfiling:
    @pytest.fixture
    def sample_df(self, sample_csv_path):
        from src.data_loader import load_csv
        return load_csv(sample_csv_path)

    def test_profile_returns_dict(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        assert isinstance(result, dict)

    def test_total_rows_correct(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        assert result["total_rows"] == 3

    def test_empty_title_count(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        assert result["empty_title"] == 0

    def test_empty_body_count(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        assert result["empty_body"] == 0

    def test_unique_original_id(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        # "001" muncul dua kali, "002" sekali → 2 unik
        assert result["unique_original_id"] == 2

    def test_entities_column_all_empty(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        ent = result["entities_column"]
        assert ent["non_empty"] == 0
        assert ent["empty"] == 3

    def test_language_distribution(self, sample_df):
        from src.profiling import profile
        result = profile(sample_df)
        lang_dist = result["language_distribution_after_dedup_original_id"]
        # Setelah dedup original_id: "001" → en, "002" → ms
        assert lang_dist.get("en", 0) >= 1
        assert lang_dist.get("ms", 0) >= 1
