from pathlib import Path

from scraper.config import load_config


def test_load_config_parses_targets(tmp_path: Path) -> None:
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

