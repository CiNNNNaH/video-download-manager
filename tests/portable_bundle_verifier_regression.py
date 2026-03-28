from pathlib import Path
import subprocess
import sys
import tempfile
import json

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_portable_bundle.py"


def test_verifier_minimum_bundle() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "data").mkdir()
        (root / "logs").mkdir()
        (root / "README.md").write_text("x", encoding="utf-8")
        (root / "CHANGELOG.md").write_text("x", encoding="utf-8")
        (root / "LICENSE").write_text("x", encoding="utf-8")
        (root / "log.txt").write_text("", encoding="utf-8")
        (root / "data" / "history.json").write_text("[]", encoding="utf-8")
        (root / "data" / "settings.json").write_text("{}", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        manifest = json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))
        assert manifest["file_count"] >= 5


if __name__ == "__main__":
    test_verifier_minimum_bundle()
    print("portable_bundle_verifier_regression passed")
