from pathlib import Path


def test_source_base_uses_english_runtime_markers():
    main_window = (Path(__file__).resolve().parents[1] / "gui" / "main_window.py").read_text(encoding="utf-8")
    assert "Yeni analiz kuyruga alindi" not in main_window
    assert "Cookie durumu:" not in main_window


def test_downloader_stage_defaults_are_english():
    downloader = (Path(__file__).resolve().parents[1] / "core" / "downloader.py").read_text(encoding="utf-8")
    assert 'stage="hazirlaniyor"' not in downloader
    assert 'stage="indiriliyor"' not in downloader
