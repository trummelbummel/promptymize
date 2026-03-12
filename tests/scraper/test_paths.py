from __future__ import annotations

from auto_prompt.scraper.paths import resolve_output_dir, sanitize_folder_name


# -- sanitize_folder_name --------------------------------------------------


def test_sanitize_clean_name_unchanged() -> None:
    assert sanitize_folder_name("my-folder_1") == "my-folder_1"


def test_sanitize_replaces_special_chars() -> None:
    assert sanitize_folder_name("my folder!v2") == "my_folder_v2"


def test_sanitize_strips_leading_trailing_underscores() -> None:
    assert sanitize_folder_name("___name___") == "name"


def test_sanitize_empty_returns_scrape() -> None:
    assert sanitize_folder_name("") == "scrape"
    assert sanitize_folder_name("   ") == "scrape"


def test_sanitize_all_special_returns_scrape() -> None:
    assert sanitize_folder_name("!!!@@@") == "scrape"


# -- resolve_output_dir ----------------------------------------------------


def test_resolve_output_dir_simple(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    out = resolve_output_dir(out_root=out_root, folder_name="docs")
    assert out == out_root.resolve() / "docs"


def test_resolve_output_dir_nested_folder(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    out = resolve_output_dir(out_root=out_root, folder_name="parent/child")
    root = out_root.resolve()
    assert str(out).startswith(str(root))
    assert out == root / "parent" / "child"


def test_resolve_output_dir_normalizes_weird_folder_name(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    out = resolve_output_dir(out_root=out_root, folder_name="../outside")
    root = out_root.resolve()
    assert str(out).startswith(str(root))
    assert "outside" in str(out)


def test_resolve_output_dir_sanitizes_each_segment(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    out = resolve_output_dir(out_root=out_root, folder_name="a b/c!d")
    root = out_root.resolve()
    assert out == root / "a_b" / "c_d"


def test_resolve_output_dir_skips_empty_segments(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()
    out = resolve_output_dir(out_root=out_root, folder_name="a//b")
    root = out_root.resolve()
    assert out == root / "a" / "b"
