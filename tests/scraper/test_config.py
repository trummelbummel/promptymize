from pathlib import Path

from auto_prompt.scraper.config import load_config


def test_load_config_parses_single_url_targets(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
targets:
  - folder_name: docs1
    url: https://example.com/a
  - folder_name: docs2
    url: https://example.com/b
""".lstrip(),
        encoding="utf-8",
    )

    parsed = load_config(cfg)
    assert [t.folder_name for t in parsed.targets] == ["docs1", "docs2"]
    assert [t.url for t in parsed.targets] == ["https://example.com/a", "https://example.com/b"]


def test_load_config_parses_url_list_targets(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
targets:
  - folder_name: research
    url:
      - https://example.com/paper-one
      - https://example.com/paper-two
""".lstrip(),
        encoding="utf-8",
    )

    parsed = load_config(cfg)
    assert len(parsed.targets) == 2
    assert parsed.targets[0].folder_name == "research/paper_one"
    assert parsed.targets[1].folder_name == "research/paper_two"
    assert parsed.targets[0].url == "https://example.com/paper-one"
    assert parsed.targets[1].url == "https://example.com/paper-two"

