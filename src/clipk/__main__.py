import sys

try:
    from .operators import init
    from .operators.flagparser import app
except ImportError:
    from clipk.operators import init
    from clipk.operators.flagparser import app


def main() -> int:
    init()  # idempotent test to check if req dirs and files are present
    # also sets up the database
    app()  # call back from run_tui + flag_parser
    return 0


if __name__ == "__main__":
    sys.exit(main())
