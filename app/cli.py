import argparse
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_server() -> int:
    from app.server import run

    run()
    return 0


def run_cron() -> int:
    from app.ingestion.sync import run_sync_job

    try:
        asyncio.run(run_sync_job())
    except Exception:
        logger.exception("sync_countries failed")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("server", help="Start the HTTP/GraphQL server.")
    subparsers.add_parser("cron", help="Run the country sync job once and exit.")

    args = parser.parse_args(argv)
    if args.command == "server":
        return run_server()
    elif args.command == "cron":
        return run_cron()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
