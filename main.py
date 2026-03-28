import sys
import traceback

from app import VDMApplication


def main() -> None:
    try:
        application = VDMApplication()
        sys.exit(application.run())
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
