from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'collect_support_bundle.py'
spec = importlib.util.spec_from_file_location('collect_support_bundle', SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_collect_support_bundle_creates_zip_with_expected_files():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / 'app'
        (root / 'logs').mkdir(parents=True)
        (root / 'data').mkdir(parents=True)
        (root / 'log.txt').write_text('root log', encoding='utf-8')
        (root / 'logs' / 'detail.log').write_text('detail', encoding='utf-8')
        (root / 'data' / 'settings.json').write_text('{}', encoding='utf-8')
        (root / 'PACKAGE_HISTORY.md').write_text('# history', encoding='utf-8')
        zip_path = module.collect_bundle(root)
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
        assert 'log.txt' in names
        assert 'logs/detail.log' in names
        assert 'data/settings.json' in names
        assert 'PACKAGE_HISTORY.md' in names


if __name__ == '__main__':
    test_collect_support_bundle_creates_zip_with_expected_files()
    print('support_bundle_regression.py passed')
