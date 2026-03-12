from __future__ import annotations

from pathlib import Path

import pytest

from auto_prompt.scraper.config import ScrapeTarget, _slug_from_url, load_config


# -- _slug_from_url --------------------------------------------------------


def test_slug_from_url_normal_path() -> None:
    assert _slug_from_url("https://example.com/docs/guide") == "guide"


def test_slug_from_url_strips_special_chars() -> None:
    assert _slug_from_url("https://example.com/my-page!v2") == "my_page_v2"


def test_slug_from_url_empty_path_uses_hostname() -> None:
    assert _slug_from_url("https://example.com") == "example_com"
    assert _slug_from_url("https://example.com/") == "example_com"


def test_slug_from_url_all_special_returns_page() -> None:
    assert _slug_from_url("https://example.com/!!!") == "page"


def test_slug_from_url_lowercases() -> None:
    assert _slug_from_url("https://example.com/MyPage") == "mypage"


# -- load_config happy paths -----------------------------------------------


def test_load_config_parses_single_url_targets(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "targets:\n"
        "  - folder_name: docs1\n"
        "    url: https://example.com/a\n"
        "  - folder_name: docs2\n"
        "    url: https://example.com/b\n",
        encoding="utf-8",
    )
    parsed = load_config(cfg)
    assert [t.folder_name for t in parsed.targets] == ["docs1", "docs2"]
    assert [t.url for t in parsed.targets] == ["https://example.com/a", "https://example.com/b"]


def test_load_config_parses_url_list_targets(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "targets:\n"
        "  - folder_name: research\n"
        "    url:\n"
        "      - https://example.com/paper-one\n"
        "      - https://example.com/paper-two\n",
        encoding="utf-8",
    )
    parsed = load_config(cfg)
    assert len(parsed.targets) == 2
    assert parsed.targets[0].folder_name == "research/paper_one"
    assert parsed.targets[1].folder_name == "research/paper_two"
    assert parsed.targets[0].url == "https://example.com/paper-one"
    assert parsed.targets[1].url == "https://example.com/paper-two"


def test_load_config_strips_whitespace(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "targets:\n"
        "  - folder_name: '  docs  '\n"
        "    url: '  https://example.com/a  '\n",
        encoding="utf-8",
    )
    parsed = load_config(cfg)
    assert parsed.targets[0].folder_name == "docs"
    assert parsed.targets[0].url == "https://example.com/a"


# -- load_config error paths -----------------------------------------------


def test_load_config_raises_on_non_dict_root(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Config root must be a mapping"):
        load_config(cfg)


def test_load_config_raises_on_missing_targets(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("something_else: true\n", encoding="utf-8")
    with pytest.raises(ValueError, match="'targets' as a list"):
        load_config(cfg)


def test_load_config_raises_on_non_list_targets(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("targets: not-a-list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="'targets' as a list"):
        load_config(cfg)


def test_load_config_raises_on_non_dict_target_item(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("targets:\n  - just_a_string\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"targets\[0\] must be a mapping"):
        load_config(cfg)


def test_load_config_raises_on_missing_folder_name(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("targets:\n  - url: https://example.com\n", encoding="utf-8")
    with pytest.raises(ValueError, match="folder_name must be a non-empty"):
        load_config(cfg)


def test_load_config_raises_on_empty_folder_name(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("targets:\n  - folder_name: '   '\n    url: https://example.com\n", encoding="utf-8")
    with pytest.raises(ValueError, match="folder_name must be a non-empty"):
        load_config(cfg)


def test_load_config_raises_on_missing_url(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("targets:\n  - folder_name: docs\n", encoding="utf-8")
    with pytest.raises(ValueError, match="url must be a non-empty string or list"):
        load_config(cfg)


def test_load_config_raises_on_empty_url_in_list(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "targets:\n"
        "  - folder_name: docs\n"
        "    url:\n"
        "      - https://example.com/a\n"
        "      - ''\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"url\[1\] must be a non-empty"):
        load_config(cfg)
