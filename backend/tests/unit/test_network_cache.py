"""Tests for the validated JSON network cache."""

from pathlib import Path

from app.routing.cache import NetworkCache
from app.routing.demo_network import build_demo_network


def test_cache_miss_hit_and_configured_directory(tmp_path: Path) -> None:
    cache_dir = tmp_path / "configured-cache"
    cache = NetworkCache(cache_dir)
    network = build_demo_network(seed=42)

    assert cache.cache_dir == cache_dir
    assert cache.load("demo") is None
    assert cache.save("demo", network) is True
    assert cache.load("demo") == network


def test_corrupted_cache_is_treated_as_a_miss(tmp_path: Path) -> None:
    cache = NetworkCache(tmp_path)
    cache.path_for("broken").write_text("not-json", encoding="utf-8")

    assert cache.load("broken") is None
    assert build_demo_network(seed=42).network_id == "demo-6-intersection"


def test_disabled_cache_has_no_side_effects(tmp_path: Path) -> None:
    cache_dir = tmp_path / "disabled-cache"
    cache = NetworkCache(cache_dir, enabled=False)

    assert cache.save("demo", build_demo_network(seed=42)) is False
    assert cache.load("demo") is None
    assert not cache_dir.exists()
