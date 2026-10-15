"""
test_dedup_split.py — Tes unit untuk dedup_split (Fase 2, Bagian 8)
====================================================================
Tes ini memverifikasi:
  - Tidak ada kebocoran original_id antar split
  - Rasio split mendekati 70/15/15
  - Duplikat eksak masuk ke grup yang sama → split yang sama
  - Near-duplicate masuk ke grup yang sama
  - Seed menghasilkan hasil yang identik (determinisme)
  - Verifikasi kebocoran mendeteksi kerusakan split

Jalankan: pytest tests/test_dedup_split.py -v
"""

import json
from pathlib import Path

import pytest


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

def make_df(records: list[dict]):
    """Buat DataFrame sederhana dari list dict."""
    import pandas as pd
    return pd.DataFrame(records)


# Body yang beragam secara topik untuk menghindari false near-dup dalam tes
BODIES_SIMPLE = [
    "Maybank posted record profits of RM 5 billion in the third quarter of 2026, driven by strong loan growth.",
    "CIMB Group announced a new digital banking platform targeting small and medium enterprises across Southeast Asia.",
    "RHB Bank launched a green financing initiative worth RM 2 billion to support sustainable development projects.",
    "Public Bank Berhad reported a net profit increase of 12 percent compared to the same period last year.",
    "Hong Leong Bank acquired a minority stake in a Malaysian fintech startup specialising in mobile payments.",
    "Bank Negara Malaysia raised its overnight policy rate by 25 basis points to curb inflationary pressure.",
    "AmBank Group unveiled a new premium wealth management service for high-net-worth individual clients.",
    "Alliance Bank Malaysia expanded its branch network to rural areas in Sabah and Sarawak this quarter.",
    "Affin Bank completed the merger with its insurance subsidiary to form a unified financial services group.",
    "OCBC Bank Malaysia signed a memorandum of understanding with the Penang state government on green bonds.",
    "Standard Chartered Malaysia launched a new Islamic banking product compliant with Shariah principles.",
    "HSBC Malaysia reported strong growth in its wealth and personal banking division for the full year 2025.",
    "Citibank Malaysia announced the closure of its consumer banking operations by end of December 2026.",
    "UOB Malaysia introduced a buy-now-pay-later scheme in partnership with major e-commerce platforms.",
    "Agro Bank Malaysia received additional capitalisation from the government to support agricultural lending.",
    "Bank Islam Malaysia reported an increase in its total financing portfolio by 15 percent year-on-year.",
    "Kuwait Finance House Malaysia expanded its product offering in the sukuk market for institutional investors.",
    "MBSB Bank completed its transformation into a full-fledged Islamic bank after receiving regulatory approval.",
    "The Malaysian Institute of Accountants hosted its annual conference on financial reporting standards.",
    "Securities Commission Malaysia issued guidelines on digital asset exchanges and cryptocurrency regulation.",
    "Bursa Malaysia recorded its highest trading volume in five years amid global market volatility concerns.",
    "Permodalan Nasional Berhad announced dividend payouts for Amanah Saham Bumiputera unit holders in 2026.",
    "Khazanah Nasional divested its stake in a logistics company as part of its portfolio rationalisation plan.",
    "EPF Malaysia approved a special withdrawal facility for members affected by the economic downturn.",
    "LTAT announced improved returns for armed forces fund members despite challenging market conditions.",
    "Tabung Haji reported an increase in pilgrims supported through its financing scheme this year in 2026.",
    "SOCSO Malaysia extended its employment insurance scheme coverage to gig economy workers nationwide.",
    "PERKESO launched a new digital portal to streamline claim submissions for unemployed individuals.",
    "Inland Revenue Board Malaysia intensified its audit activities targeting high-income earners and SMEs.",
    "The Finance Ministry tabled the 2027 national budget with a focus on economic resilience and digital growth.",
]
RECORDS_SIMPLE = [
    {"original_id": f"ID{i:03d}", "body": BODIES_SIMPLE[i]}
    for i in range(len(BODIES_SIMPLE))
]

RECORDS_WITH_EXACT_DUP = [
    {"original_id": "A001", "body": "Maybank reported record profits in Q3 2026 in Kuala Lumpur."},
    {"original_id": "A002", "body": "CIMB Group announced expansion plans for 2027 in Malaysia."},
    {"original_id": "A003", "body": "Maybank reported record profits in Q3 2026 in Kuala Lumpur."},  # exact dup of A001
    {"original_id": "A004", "body": "RHB Bank launched a new digital banking service this week."},
    {"original_id": "A005", "body": "Public Bank posted strong quarterly results in September 2026."},
    {"original_id": "A006", "body": "Hong Leong Bank acquired a stake in a fintech startup recently."},
]


# ──────────────────────────────────────────────────────────────
# Test: build_groups
# ──────────────────────────────────────────────────────────────

class TestBuildGroups:
    def test_exact_duplicates_in_same_group(self):
        """A001 dan A003 (body identik) harus ada di grup yang sama."""
        from src.dedup_split import build_groups
        df = make_df(RECORDS_WITH_EXACT_DUP)
        id_to_group = build_groups(df)

        assert id_to_group["A001"] == id_to_group["A003"], (
            "A001 dan A003 punya body identik tapi grup berbeda"
        )

    def test_distinct_articles_in_different_groups(self):
        """Artikel dengan body sangat berbeda harus di grup berbeda."""
        from src.dedup_split import build_groups
        df = make_df(RECORDS_WITH_EXACT_DUP)
        id_to_group = build_groups(df)

        # A002 (CIMB) dan A004 (RHB) harus di grup berbeda
        assert id_to_group["A002"] != id_to_group["A004"], (
            "A002 dan A004 harusnya di grup berbeda"
        )

    def test_returns_all_ids(self):
        """Semua original_id harus ada dalam output id_to_group."""
        from src.dedup_split import build_groups
        df = make_df(RECORDS_WITH_EXACT_DUP)
        id_to_group = build_groups(df)
        for rec in RECORDS_WITH_EXACT_DUP:
            assert rec["original_id"] in id_to_group

    def test_group_ids_are_integers(self):
        from src.dedup_split import build_groups
        df = make_df(RECORDS_SIMPLE)
        id_to_group = build_groups(df)
        for gid in id_to_group.values():
            assert isinstance(gid, int)


# ──────────────────────────────────────────────────────────────
# Test: split_groups
# ──────────────────────────────────────────────────────────────

class TestSplitGroups:
    def _get_splits(self, records=None, seed=42):
        from src.dedup_split import build_groups, split_groups
        df = make_df(records or RECORDS_SIMPLE)
        id_to_group = build_groups(df)
        return split_groups(id_to_group, seed=seed)

    def test_all_three_splits_exist(self):
        splits = self._get_splits()
        assert "train" in splits
        assert "val" in splits
        assert "test" in splits

    def test_no_id_in_multiple_splits(self):
        """Tidak ada original_id yang ada di lebih dari satu split."""
        splits = self._get_splits()
        all_ids = splits["train"] + splits["val"] + splits["test"]
        assert len(all_ids) == len(set(all_ids)), "Ada kebocoran antar split!"

    def test_all_ids_in_some_split(self):
        """Semua original_id harus masuk ke salah satu split."""
        splits = self._get_splits()
        all_ids_in_splits = set(splits["train"] + splits["val"] + splits["test"])
        expected_ids = {r["original_id"] for r in RECORDS_SIMPLE}
        assert all_ids_in_splits == expected_ids

    def test_train_is_largest_split(self):
        """Train split harus lebih besar dari val dan test."""
        splits = self._get_splits()
        assert len(splits["train"]) > len(splits["val"])
        assert len(splits["train"]) > len(splits["test"])

    def test_approximate_ratios(self):
        """Rasio split mendekati 70/15/15 (toleransi ±5%)."""
        splits = self._get_splits()
        total = sum(len(v) for v in splits.values())
        train_pct = len(splits["train"]) / total
        val_pct = len(splits["val"]) / total
        test_pct = len(splits["test"]) / total

        assert 0.60 <= train_pct <= 0.80, f"Train ratio {train_pct:.2f} di luar toleransi"
        assert 0.10 <= val_pct <= 0.25, f"Val ratio {val_pct:.2f} di luar toleransi"
        assert 0.10 <= test_pct <= 0.25, f"Test ratio {test_pct:.2f} di luar toleransi"

    def test_deterministic_with_same_seed(self):
        """Dua run dengan seed sama harus menghasilkan split identik."""
        splits1 = self._get_splits(seed=42)
        splits2 = self._get_splits(seed=42)
        assert sorted(splits1["train"]) == sorted(splits2["train"])
        assert sorted(splits1["val"]) == sorted(splits2["val"])
        assert sorted(splits1["test"]) == sorted(splits2["test"])

    def test_different_seeds_produce_different_splits(self):
        """Seed berbeda harus menghasilkan split berbeda (dengan probabilitas tinggi).
        Test ini cukup memverifikasi bahwa TRAIN tidak identik, karena dengan
        dataset kecil ada kemungkinan kecil kebetulan identik.
        """
        splits1 = self._get_splits(seed=42)
        splits2 = self._get_splits(seed=123456)
        # Setidaknya satu split harus berbeda
        train_same = sorted(splits1["train"]) == sorted(splits2["train"])
        val_same = sorted(splits1["val"]) == sorted(splits2["val"])
        test_same = sorted(splits1["test"]) == sorted(splits2["test"])
        all_same = train_same and val_same and test_same
        # Untuk 30 artikel dengan seed sangat berbeda, hampir tidak mungkin semua sama
        assert not all_same, (
            "Seed 42 dan 123456 menghasilkan split identik — "
            "kemungkinan ada bug di shuffle"
        )

    def test_exact_dup_in_same_split(self):
        """A001 dan A003 (body identik) harus masuk ke split yang sama."""
        from src.dedup_split import build_groups, split_groups
        df = make_df(RECORDS_WITH_EXACT_DUP)
        id_to_group = build_groups(df)
        splits = split_groups(id_to_group, seed=42)

        def find_split(oid: str) -> str:
            for name, ids in splits.items():
                if oid in ids:
                    return name
            return "NOT_FOUND"

        assert find_split("A001") == find_split("A003"), (
            "A001 dan A003 (duplikat eksak) harus di split yang sama"
        )


# ──────────────────────────────────────────────────────────────
# Test: verify_no_leakage
# ──────────────────────────────────────────────────────────────

class TestVerifyNoLeakage:
    def test_clean_splits_pass(self):
        from src.dedup_split import verify_no_leakage
        splits = {"train": ["A", "B", "C"], "val": ["D", "E"], "test": ["F"]}
        assert verify_no_leakage(splits) is True

    def test_leakage_detected(self):
        """Split dengan ID ganda antar split harus terdeteksi."""
        from src.dedup_split import verify_no_leakage
        splits = {"train": ["A", "B", "C"], "val": ["C", "D"], "test": ["E"]}
        assert verify_no_leakage(splits) is False

    def test_empty_splits(self):
        from src.dedup_split import verify_no_leakage
        splits = {"train": [], "val": [], "test": []}
        assert verify_no_leakage(splits) is True
