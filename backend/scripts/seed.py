"""
Database seeder — creates the default single user and initial source configs.

Run with: make seed   (or: docker compose exec api uv run python scripts/seed.py)

This script is idempotent: safe to run multiple times.
"""

import asyncio
import sys

# Ensure the app package is importable when run directly
sys.path.insert(0, "/app")


async def main() -> None:
    print("Seeding database...")
    # TODO (Step 4): seed default user (id=1) and example sources
    print("Done. (No models to seed yet — implement in Step 4)")


if __name__ == "__main__":
    asyncio.run(main())
