import sys

try:
    from .operators import init, wait
    from .operators.flagparser import app
except ImportError:
    from clipk.operators import init, wait
    from clipk.operators.flagparser import app


def main() -> int:
    
    init()  # idempotent test to check if req dirs and files are present

    try:
        app()

    finally:
        wait()
    return 0


if __name__ == "__main__":
    sys.exit(main())
