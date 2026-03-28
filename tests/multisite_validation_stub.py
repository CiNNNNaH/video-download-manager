from pathlib import Path


def run() -> None:
    docs = [
        Path(__file__).resolve().parents[1] / 'docs' / 'MULTI_SITE_VALIDATION_MATRIX.md',
        Path(__file__).resolve().parents[1] / 'docs' / 'CONTROLLED_USER_TEST_PLAN.md',
        Path(__file__).resolve().parents[1] / 'docs' / 'CURRENT_BEHAVIOR_CONTRACT.md',
    ]
    missing = [str(p) for p in docs if not p.exists()]
    if missing:
        raise SystemExit(f'Missing validation docs: {missing}')
    print('multi-site validation stub passed')
    print('Use docs/MULTI_SITE_VALIDATION_MATRIX.md as the manual validation checklist.')


if __name__ == '__main__':
    run()
