from pathlib import Path


def run() -> None:
    root = Path(__file__).resolve().parents[1]
    required = [
        root / 'docs' / 'FINAL_RELEASE_CHECKLIST.md',
        root / 'docs' / 'PORTABLE_BUNDLE_STRUCTURE.md',
        root / 'scripts' / 'run_final_release_gate.bat',
        root / 'scripts' / 'clean_runtime_artifacts.bat',
        root / 'PACKAGE_14_NOTES.md',
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit('missing final release files: ' + ', '.join(missing))
    print('final release stub passed')


if __name__ == '__main__':
    run()
