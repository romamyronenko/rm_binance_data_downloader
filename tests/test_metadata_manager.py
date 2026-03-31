import json

import pytest

from rm_bdd.metadata_manager import MetadataManager


def test_initial_metadata_empty(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    assert mm.data == {}


def test_update_creates_structure(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    assert mm.data["BTCUSDT"]["1m"] == ["2024-01"]


def test_update_saves_to_file(tmp_path):
    path = tmp_path / "meta.json"
    mm = MetadataManager(str(path))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    with open(path) as f:
        data = json.load(f)
    assert data["BTCUSDT"]["1m"] == ["2024-01"]


def test_update_no_duplicate(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    assert mm.data["BTCUSDT"]["1m"] == ["2024-01"]


def test_update_multiple_dates(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    mm.update_metadata("BTCUSDT", "1m", "2024-02")
    assert mm.data["BTCUSDT"]["1m"] == ["2024-01", "2024-02"]


def test_update_multiple_symbols(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    mm.update_metadata("ETHUSDT", "1m", "2024-01")
    assert "BTCUSDT" in mm.data
    assert "ETHUSDT" in mm.data


def test_check_returns_true_when_not_present(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    assert mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01") is True


def test_check_returns_false_when_present(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    assert mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01") is False


def test_check_daily_skipped_if_month_present(tmp_path):
    """Якщо місяць вже є в метаданих — денні файли цього місяця пропускаються."""
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-01")
    assert mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01-15") is False


def test_check_daily_passes_if_month_not_present(tmp_path):
    mm = MetadataManager(str(tmp_path / "meta.json"))
    mm.update_metadata("BTCUSDT", "1m", "2024-02")
    assert mm.check_date_not_in_metadata("BTCUSDT", "1m", "2024-01-15") is True


def test_loads_existing_metadata_from_file(tmp_path):
    path = tmp_path / "meta.json"
    data = {"BTCUSDT": {"1m": ["2024-01", "2024-02"]}}
    path.write_text(json.dumps(data))
    mm = MetadataManager(str(path))
    assert mm.data["BTCUSDT"]["1m"] == ["2024-01", "2024-02"]


def test_missing_file_returns_empty(tmp_path):
    mm = MetadataManager(str(tmp_path / "nonexistent.json"))
    assert mm.data == {}
