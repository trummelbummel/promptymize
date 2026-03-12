from auto_prompt.scraper.paths import resolve_output_dir


def test_resolve_output_dir_normalizes_weird_folder_name(tmp_path) -> None:
    out_root = tmp_path / "resources"
    out_root.mkdir()

    # Even if the name contains traversal-looking pieces, the helper should normalize it
    # into a safe subdirectory of out_root.
    out = resolve_output_dir(out_root=out_root, folder_name="../outside")
    assert out.parent == out_root.resolve()
    assert "outside" in str(out)

