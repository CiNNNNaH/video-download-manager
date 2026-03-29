from pathlib import Path


def test_main_window_has_no_remaining_turkish_ui_literals():
    text = Path("gui/main_window.py").read_text(encoding="utf-8")
    banned = [
        "Once bir link gir.",
        "Son linkler",
        "Thumbnail yuklenemedi",
        "Toplam format gorunumu",
        "Once bir format sec.",
        "Kullanici indirmeyi durdurmak istedi",
        "Cikti:",
        "VDM ayri bir CMD penceresinde",
        "Bu surec VDM tarafindan",
        "Islem tamamlandi. Bu pencereyi kapatabilirsin.",
        "FFmpeg ile Re-encode Et",
    ]
    for item in banned:
        assert item not in text


def test_main_window_has_no_known_localization_regression_tokens():
    text = Path("gui/main_window.py").read_text(encoding="utf-8")
    banned = [
        'fself.t(',
        'status.status == "cancelled"',
        'QLabel("Container")',
    ]
    for item in banned:
        assert item not in text
