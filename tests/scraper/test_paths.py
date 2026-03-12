from auto_prompt.scraper.paths import resolve_output_dir


def test_resolve_output_dir_normalizes_weird_folder_name(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()

    out = resolve_output_dir(out_root=out_root, folder_name="../outside")
    root = out_root.resolve()
    assert str(out).startswith(str(root))
    assert "outside" in str(out)


def test_resolve_output_dir_nested_folder(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()

    out = resolve_output_dir(out_root=out_root, folder_name="parent/child")
    root = out_root.resolve()
    assert str(out).startswith(str(root))
    assert out == root / "parent" / "child"

